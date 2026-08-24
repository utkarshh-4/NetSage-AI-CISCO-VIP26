"""Tests for AI diagnosis module."""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from ai.diagnose import AIDiagnosisEngine, diagnose_case
from ai.schemas import DiagnosisResponse, DiagnosisError
from openai import AuthenticationError, RateLimitError, APIError


class TestAIDiagnosisEngine:
    """Test suite for AIDiagnosisEngine."""
    
    def test_init_with_api_key(self):
        """Test initialization with API key."""
        engine = AIDiagnosisEngine(api_key="test-key")
        assert engine.api_key == "test-key"
        assert engine.model == "gpt-3.5-turbo"  # default
    
    def test_init_without_api_key_raises_error(self):
        """Test that initialization without API key raises ValueError."""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="OpenAI API key not provided"):
                AIDiagnosisEngine()
    
    def test_init_with_custom_model(self):
        """Test initialization with custom model."""
        engine = AIDiagnosisEngine(api_key="test-key", model="gpt-3.5-turbo")
        assert engine.model == "gpt-3.5-turbo"
    
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'})
    def test_init_from_env_var(self):
        """Test initialization from environment variable."""
        engine = AIDiagnosisEngine()
        assert engine.api_key == "test-key"


class TestDiagnoseCase:
    """Test suite for diagnose_case function."""
    
    def test_diagnose_case_with_valid_response(self):
        """Test successful diagnosis with valid AI response."""
        mock_response = {
            "root_cause": "Interface is administratively down",
            "confidence": "high",
            "evidence": [
                {
                    "source": "show_outputs",
                    "content": "administratively down",
                    "type": "observed"
                }
            ],
            "next_command": None,
            "fix_steps": [],
            "osi_layer": "Layer 3",
            "issue_type": "routing",
            "severity": "high",
            "alternative_causes": [],
            "limitations": [],
            "requires_human_review": True
        }
        
        case = {
            "case_id": "TEST-001",
            "symptom": "Test symptom",
            "topology_note": "Test topology",
            "show_outputs": "administratively down",
            "expected_fault": "Test fault",
            "osi_layer": "Layer 3",
            "concept_tag": "Test",
            "severity": "High"
        }
        
        with patch('ai.diagnose.AIDiagnosisEngine') as MockEngine:
            mock_engine = Mock()
            mock_instance = Mock()
            mock_instance.diagnose_case.return_value = DiagnosisResponse(**mock_response)
            MockEngine.return_value = mock_instance
            
            result = diagnose_case(case, api_key="test-key")
            
            assert isinstance(result, DiagnosisResponse)
            assert result.root_cause == "Interface is administratively down"
    
    def test_diagnose_case_without_api_key(self):
        """Test diagnosis without API key returns error."""
        case = {"case_id": "TEST-001"}
        
        with patch.dict('os.environ', {}, clear=True):
            result = diagnose_case(case)
            
            assert isinstance(result, DiagnosisError)
            assert result.error_type == "configuration_error"
    
    def test_diagnose_case_with_provided_rule_results(self):
        """Test that provided rule results are used instead of running checks."""
        case = {
            "case_id": "TEST-001",
            "symptom": "Test",
            "topology_note": "Test",
            "show_outputs": "Test",
            "expected_fault": "Test",
            "osi_layer": "Layer 3",
            "concept_tag": "Test",
            "severity": "High"
        }
        
        mock_response = {
            "root_cause": "Test",
            "confidence": "high",
            "evidence": [{"source": "test", "content": "test", "type": "observed"}],
            "osi_layer": "Layer 3",
            "issue_type": "test",
            "severity": "high"
        }
        
        provided_rule_results = {"test_check": {"status": "DETECTED"}}
        
        with patch('ai.diagnose.run_all_checks') as mock_checks:
            with patch('ai.diagnose.AIDiagnosisEngine.__init__', return_value=None):
                with patch('ai.diagnose.AIDiagnosisEngine.diagnose_case') as mock_diagnose:
                    mock_diagnose.return_value = DiagnosisResponse(**mock_response)
                    
                    diagnose_case(case, rule_results=provided_rule_results, api_key="test-key")
                    
                    # Should not call run_all_checks when rule_results are provided
                    mock_checks.assert_not_called()
                    # Should call diagnose_case with the provided rule results
                    mock_diagnose.assert_called_once_with(case, provided_rule_results)


class TestAPIErrorHandling:
    """Test suite for API error handling."""
    
    def test_authentication_error(self):
        """Test handling of authentication errors."""
        case = {
            "case_id": "TEST-001",
            "symptom": "Test",
            "topology_note": "Test",
            "show_outputs": "Test",
            "expected_fault": "Test",
            "osi_layer": "Layer 3",
            "concept_tag": "Test",
            "severity": "High"
        }
        
        with patch('ai.diagnose.OpenAI') as MockOpenAI:
            mock_client = Mock()
            mock_client.chat.completions.create.side_effect = Exception("Authentication failed")
            MockOpenAI.return_value = mock_client
            
            engine = AIDiagnosisEngine(api_key="test-key")
            result = engine.diagnose_case(case)
            
            assert isinstance(result, DiagnosisError)
            assert result.error_type == "unexpected_error"
    
    def test_rate_limit_error(self):
        """Test handling of rate limit errors."""
        case = {
            "case_id": "TEST-001",
            "symptom": "Test",
            "topology_note": "Test",
            "show_outputs": "Test",
            "expected_fault": "Test",
            "osi_layer": "Layer 3",
            "concept_tag": "Test",
            "severity": "High"
        }
        
        with patch('ai.diagnose.OpenAI') as MockOpenAI:
            mock_client = Mock()
            mock_client.chat.completions.create.side_effect = Exception("Rate limit exceeded")
            MockOpenAI.return_value = mock_client
            
            engine = AIDiagnosisEngine(api_key="test-key")
            result = engine.diagnose_case(case)
            
            assert isinstance(result, DiagnosisError)
            assert result.error_type == "unexpected_error"
    
    def test_api_error(self):
        """Test handling of general API errors."""
        case = {
            "case_id": "TEST-001",
            "symptom": "Test",
            "topology_note": "Test",
            "show_outputs": "Test",
            "expected_fault": "Test",
            "osi_layer": "Layer 3",
            "concept_tag": "Test",
            "severity": "High"
        }
        
        with patch('ai.diagnose.OpenAI') as MockOpenAI:
            mock_client = Mock()
            mock_client.chat.completions.create.side_effect = Exception("API error")
            MockOpenAI.return_value = mock_client
            
            engine = AIDiagnosisEngine(api_key="test-key")
            result = engine.diagnose_case(case)
            
            assert isinstance(result, DiagnosisError)
            assert result.error_type == "unexpected_error"


class TestMalformedResponseHandling:
    """Test suite for malformed response handling."""
    
    def test_invalid_json_response(self):
        """Test handling of invalid JSON response."""
        case = {
            "case_id": "TEST-001",
            "symptom": "Test",
            "topology_note": "Test",
            "show_outputs": "Test",
            "expected_fault": "Test",
            "osi_layer": "Layer 3",
            "concept_tag": "Test",
            "severity": "High"
        }
        
        with patch('ai.diagnose.OpenAI') as MockOpenAI:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "This is not valid JSON"
            mock_client.chat.completions.create.return_value = mock_response
            MockOpenAI.return_value = mock_client
            
            engine = AIDiagnosisEngine(api_key="test-key")
            result = engine.diagnose_case(case)
            
            assert isinstance(result, DiagnosisError)
            assert result.error_type == "malformed_response"
    
    def test_missing_required_field_in_response(self):
        """Test handling of response with missing required fields."""
        case = {
            "case_id": "TEST-001",
            "symptom": "Test",
            "topology_note": "Test",
            "show_outputs": "Test",
            "expected_fault": "Test",
            "osi_layer": "Layer 3",
            "concept_tag": "Test",
            "severity": "High"
        }
        
        invalid_response = {
            "root_cause": "Test",
            # Missing required fields: confidence, evidence, osi_layer, issue_type, severity
        }
        
        with patch('ai.diagnose.OpenAI') as MockOpenAI:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = json.dumps(invalid_response)
            mock_client.chat.completions.create.return_value = mock_response
            MockOpenAI.return_value = mock_client
            
            engine = AIDiagnosisEngine(api_key="test-key")
            result = engine.diagnose_case(case)
            
            assert isinstance(result, DiagnosisError)
            assert result.error_type == "unexpected_error"
    
    def test_empty_evidence_in_response(self):
        """Test handling of response with empty evidence list."""
        case = {
            "case_id": "TEST-001",
            "symptom": "Test",
            "topology_note": "Test",
            "show_outputs": "Test",
            "expected_fault": "Test",
            "osi_layer": "Layer 3",
            "concept_tag": "Test",
            "severity": "High"
        }
        
        invalid_response = {
            "root_cause": "Test",
            "confidence": "high",
            "evidence": [],  # Empty evidence is invalid
            "osi_layer": "Layer 3",
            "issue_type": "test",
            "severity": "high"
        }
        
        with patch('ai.diagnose.OpenAI') as MockOpenAI:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = json.dumps(invalid_response)
            mock_client.chat.completions.create.return_value = mock_response
            MockOpenAI.return_value = mock_client
            
            engine = AIDiagnosisEngine(api_key="test-key")
            result = engine.diagnose_case(case)
            
            assert isinstance(result, DiagnosisError)
            assert result.error_type == "unexpected_error"
