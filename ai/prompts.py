"""Prompt management for AI diagnosis."""

from pathlib import Path
from typing import Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PromptManager:
    """Manages loading and formatting prompts for AI diagnosis."""
    
    def __init__(self, prompt_path: str = "prompts/diagnose_prompt.md"):
        """
        Initialize the prompt manager.
        
        Args:
            prompt_path: Path to the prompt template file
        """
        self.prompt_path = Path(prompt_path)
        self.system_prompt = self._load_system_prompt()
    
    def _load_system_prompt(self) -> str:
        """
        Load the system prompt from file.
        
        Returns:
            System prompt string
            
        Raises:
            FileNotFoundError: If prompt file does not exist
        """
        if not self.prompt_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {self.prompt_path.absolute()}")
        
        with open(self.prompt_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        logger.info(f"Loaded system prompt from {self.prompt_path.absolute()}")
        return content
    
    def format_user_prompt(self, case: Dict[str, str], rule_results: Dict[str, Any]) -> str:
        """
        Format the user prompt with case data and rule results.
        
        Args:
            case: Dictionary containing case data
            rule_results: Dictionary containing rule checker results
            
        Returns:
            Formatted user prompt string
        """
        prompt_parts = [
            "## Case Information",
            "",
            f"**Case ID:** {case.get('case_id', 'UNKNOWN')}",
            f"**Symptom:** {case.get('symptom', 'Not provided')}",
            f"**Topology Note:** {case.get('topology_note', 'Not provided')}",
            f"**Show Outputs:** {case.get('show_outputs', 'Not provided')}",
            f"**Expected Fault:** {case.get('expected_fault', 'Not provided')}",
            f"**OSI Layer:** {case.get('osi_layer', 'Not provided')}",
            f"**Concept Tag:** {case.get('concept_tag', 'Not provided')}",
            f"**Severity:** {case.get('severity', 'Not provided')}",
            "",
            "## Deterministic Rule Checker Results",
            ""
        ]
        
        for check_name, result in rule_results.items():
            if isinstance(result, dict):
                status = result.get('status', 'UNKNOWN')
                evidence = result.get('evidence', [])
                prompt_parts.append(f"**{check_name}:** {status}")
                if evidence:
                    prompt_parts.append(f"  Evidence: {', '.join(evidence)}")
            else:
                prompt_parts.append(f"**{check_name}:** {result}")
            prompt_parts.append("")
        
        prompt_parts.append("Please analyze this case and provide a diagnosis in the specified JSON format.")
        
        return "\n".join(prompt_parts)
    
    def get_system_prompt(self) -> str:
        """
        Get the system prompt.
        
        Returns:
            System prompt string
        """
        return self.system_prompt
    
    def reload_prompt(self) -> None:
        """Reload the system prompt from file."""
        self.system_prompt = self._load_system_prompt()
        logger.info("System prompt reloaded")


def get_prompt_manager(prompt_path: str = "prompts/diagnose_prompt.md") -> PromptManager:
    """
    Convenience function to get a PromptManager instance.
    
    Args:
        prompt_path: Path to the prompt template file
        
    Returns:
        PromptManager instance
    """
    return PromptManager(prompt_path)
