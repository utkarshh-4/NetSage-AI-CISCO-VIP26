"""AI diagnosis module for network troubleshooting."""

import os
import json
import logging
from typing import Dict, Any, Union
from openai import OpenAI, OpenAIError, APIError, RateLimitError, AuthenticationError, PermissionDeniedError
from dotenv import load_dotenv

from ai.schemas import DiagnosisResponse, DiagnosisError
from ai.prompts import PromptManager
from rules.checker import run_all_checks

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables (override stale shell env vars with .env file)
load_dotenv(override=True)


class AIDiagnosisEngine:
    """Engine for AI-powered network diagnosis."""
    
    def __init__(self, api_key: str = None, model: str = None, provider: str = None, base_url: str = None):
        """
        Initialize the AI diagnosis engine.
        
        Args:
            api_key: API key (if None, loads from provider-specific env var)
            model: Model to use (if None, loads from provider-specific env var or default)
            provider: AI provider ('openai' or 'anthropic', defaults to 'openai')
            base_url: Base URL for OpenAI-compatible endpoints (e.g. OpenRouter)
        """
        self.provider = provider or os.getenv("AI_PROVIDER", "openai").lower()
        
        if self.provider == "anthropic":
            self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
            self.model = model or os.getenv("ANTHROPIC_MODEL", "claude-3-haiku-20240307")
            
            if not self.api_key:
                raise ValueError("Anthropic API key not provided. Set ANTHROPIC_API_KEY environment variable.")
            
            # Import anthropic only when needed
            try:
                from anthropic import Anthropic
                self.client = Anthropic(api_key=self.api_key)
            except ImportError:
                raise ImportError("anthropic package not installed. Install with: pip install anthropic")
            
        else:  # OpenAI (default)
            self.api_key = api_key or os.getenv("OPENAI_API_KEY")
            self.model = model or os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
            
            if not self.api_key:
                raise ValueError("OpenAI API key not provided. Set OPENAI_API_KEY environment variable.")
            
            # Detect or load base URL (e.g. for OpenRouter or custom endpoint)
            resolved_base_url = base_url or os.getenv("OPENAI_BASE_URL")
            if not resolved_base_url and self.api_key.startswith("sk-or-v1-"):
                resolved_base_url = "https://openrouter.ai/api/v1"
            
            if resolved_base_url:
                self.client = OpenAI(api_key=self.api_key, base_url=resolved_base_url)
            else:
                self.client = OpenAI(api_key=self.api_key)
        
        self.prompt_manager = PromptManager()
        
        logger.info(f"AI Diagnosis Engine initialized with provider: {self.provider}, model: {self.model}")
    
    def diagnose_case(
        self,
        case: Dict[str, str],
        rule_results: Dict[str, Any] = None
    ) -> Union[DiagnosisResponse, DiagnosisError]:
        """
        Diagnose a network troubleshooting case using AI.
        
        Args:
            case: Dictionary containing case data
            rule_results: Dictionary containing rule checker results (if None, will run checks)
            
        Returns:
            DiagnosisResponse if successful, DiagnosisError if failed
        """
        try:
            # Run rule checks if not provided
            if rule_results is None:
                logger.info("Running deterministic rule checks")
                rule_check_results = run_all_checks(case)
                rule_results = {
                    result.check_name: result.to_dict()
                    for result in rule_check_results
                }
            
            # Format prompts
            system_prompt = self.prompt_manager.get_system_prompt()
            user_prompt = self.prompt_manager.format_user_prompt(case, rule_results)
            
            logger.info(f"Calling {self.provider} API for case {case.get('case_id', 'UNKNOWN')}")
            
            # Call appropriate API
            if self.provider == "anthropic":
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=2000,
                    system=system_prompt,
                    messages=[
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.3
                )
                response_content = response.content[0].text
            else:  # OpenAI
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.3,
                    response_format={"type": "json_object"}
                )
                response_content = response.choices[0].message.content
            
            logger.info(f"Received response from {self.provider} API for case {case.get('case_id', 'UNKNOWN')}")
            
            # Parse and validate response
            diagnosis_dict = json.loads(response_content)
            diagnosis = DiagnosisResponse(**diagnosis_dict)
            
            logger.info(f"Diagnosis validated successfully for case {case.get('case_id', 'UNKNOWN')}")
            
            return diagnosis
            
        except AuthenticationError as e:
            logger.error(f"Authentication error: {e}")
            return DiagnosisError(
                error_type="authentication_error",
                message=f"Invalid {self.provider} API key or authentication failed",
                details={"str_error": str(e)},
                retry_possible=False
            )
        
        except PermissionDeniedError as e:
            logger.error(f"Permission / Limit error: {e}")
            return DiagnosisError(
                error_type="permission_denied_error",
                message=f"{self.provider} API key limit or permission error: {str(e)}",
                details={"str_error": str(e)},
                retry_possible=False
            )
        
        except RateLimitError as e:
            logger.error(f"Rate limit error: {e}")
            return DiagnosisError(
                error_type="rate_limit_error",
                message=f"{self.provider} API rate limit exceeded",
                details={"str_error": str(e)},
                retry_possible=True
            )
        
        except APIError as e:
            logger.error(f"{self.provider} API error: {e}")
            return DiagnosisError(
                error_type="api_error",
                message=f"{self.provider} API returned an error",
                details={"str_error": str(e)},
                retry_possible=True
            )
        
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return DiagnosisError(
                error_type="malformed_response",
                message="AI response was not valid JSON",
                details={"str_error": str(e), "response_content": response_content if 'response_content' in locals() else None},
                retry_possible=True
            )
        
        except Exception as e:
            error_str = str(e)
            if "anthropic" in str(type(e).__module__).lower() or "anthropic" in error_str.lower():
                logger.error(f"Anthropic API error: {e}")
                return DiagnosisError(
                    error_type="api_error",
                    message="Anthropic API returned an error",
                    details={"str_error": str(e)},
                    retry_possible=True
                )
            
            logger.error(f"Unexpected error during diagnosis: {e}")
            return DiagnosisError(
                error_type="unexpected_error",
                message=f"Unexpected error: {str(e)}",
                details={"str_error": str(e), "error_type": type(e).__name__},
                retry_possible=True
            )


def diagnose_case(
    case: Dict[str, str],
    rule_results: Dict[str, Any] = None,
    api_key: str = None,
    model: str = None,
    provider: str = None,
    base_url: str = None
) -> Union[DiagnosisResponse, DiagnosisError]:
    """
    Convenience function to diagnose a case.
    
    Args:
        case: Dictionary containing case data
        rule_results: Dictionary containing rule checker results (optional)
        api_key: API key (optional, loads from env var if not provided)
        model: Model to use (optional, loads from env var if not provided)
        provider: AI provider ('openai' or 'anthropic', optional)
        base_url: Base URL for OpenAI-compatible endpoints (optional)
        
    Returns:
        DiagnosisResponse if successful, DiagnosisError if failed
    """
    try:
        engine = AIDiagnosisEngine(api_key=api_key, model=model, provider=provider, base_url=base_url)
        return engine.diagnose_case(case, rule_results)
    except ValueError as e:
        return DiagnosisError(
            error_type="configuration_error",
            message=str(e),
            retry_possible=False
        )
