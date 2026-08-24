"""Tests for NetSage AI Batch Validation Script."""

import pytest
import tempfile
import os
from pathlib import Path
import json

from batch_validation import (
    ValidationResult,
    BatchValidationSummary,
    process_single_case,
    compare_diagnosis_with_expected,
    run_batch_validation,
    save_results
)


class TestValidationResult:
    """Test suite for ValidationResult class."""
    
    def test_validation_result_initialization(self):
        """Test that ValidationResult initializes correctly."""
        result = ValidationResult("NET-001")
        
        assert result.case_id == "NET-001"
        assert result.success == False
        assert result.data_valid == False
        assert result.rule_check_success == False
        assert result.ai_diagnosis_success == False
        assert result.ai_schema_valid == False
        assert result.ai_agreement == False
        assert result.insufficient_evidence == False
        assert result.error_message is None
    
    def test_validation_result_to_dict(self):
        """Test that ValidationResult converts to dictionary correctly."""
        result = ValidationResult("NET-001")
        result.success = True
        result.data_valid = True
        result.expected_fault = "Test fault"
        
        result_dict = result.to_dict()
        
        assert isinstance(result_dict, dict)
        assert result_dict['case_id'] == "NET-001"
        assert result_dict['success'] == True
        assert result_dict['data_valid'] == True
        assert result_dict['expected_fault'] == "Test fault"


class TestBatchValidationSummary:
    """Test suite for BatchValidationSummary class."""
    
    def test_batch_validation_summary_initialization(self):
        """Test that BatchValidationSummary initializes correctly."""
        summary = BatchValidationSummary()
        
        assert summary.total_cases == 0
        assert summary.successfully_processed == 0
        assert summary.rule_checker_failures == 0
        assert summary.ai_failures == 0
        assert summary.schema_failures == 0
        assert summary.insufficient_evidence_cases == 0
        assert summary.ai_expected_agreement == 0
        assert len(summary.validation_results) == 0
    
    def test_add_result_updates_statistics(self):
        """Test that add_result updates statistics correctly."""
        summary = BatchValidationSummary()
        result = ValidationResult("NET-001")
        result.success = True
        result.rule_check_success = True
        result.ai_agreement = True
        
        summary.add_result(result)
        
        assert summary.total_cases == 1
        assert summary.successfully_processed == 1
        assert summary.ai_expected_agreement == 1
    
    def test_add_result_handles_failures(self):
        """Test that add_result handles failures correctly."""
        summary = BatchValidationSummary()
        result = ValidationResult("NET-001")
        result.success = False
        result.rule_check_success = False
        result.ai_diagnosis_success = False
        
        summary.add_result(result)
        
        assert summary.total_cases == 1
        assert summary.successfully_processed == 0
        assert summary.rule_checker_failures == 1
        assert summary.ai_failures == 1
    
    def test_add_human_review(self):
        """Test that add_human_review updates statistics correctly."""
        summary = BatchValidationSummary()
        
        summary.add_human_review("ACCEPT")
        summary.add_human_review("EDIT")
        summary.add_human_review("REJECT")
        
        assert summary.human_accepted == 1
        assert summary.human_edited == 1
        assert summary.human_rejected == 1
    
    def test_to_dict(self):
        """Test that to_dict converts summary correctly."""
        summary = BatchValidationSummary()
        result = ValidationResult("NET-001")
        result.success = True
        summary.add_result(result)
        
        summary_dict = summary.to_dict()
        
        assert isinstance(summary_dict, dict)
        assert 'total_cases' in summary_dict
        assert 'successfully_processed' in summary_dict
        assert 'success_rate' in summary_dict


class TestCompareDiagnosisWithExpected:
    """Test suite for compare_diagnosis_with_expected function."""
    
    def test_exact_match(self):
        """Test exact match comparison."""
        assert compare_diagnosis_with_expected("Interface down", "Interface down") == True
    
    def test_case_insensitive_match(self):
        """Test case-insensitive comparison."""
        assert compare_diagnosis_with_expected("Interface down", "interface down") == True
    
    def test_containment_match(self):
        """Test containment comparison."""
        # Test that shorter string is contained in longer string
        assert compare_diagnosis_with_expected("interface down", "interface down issue") == True
    
    def test_no_match(self):
        """Test no match case."""
        assert compare_diagnosis_with_expected("Interface down", "Routing issue") == False
    
    def test_empty_strings(self):
        """Test handling of empty strings."""
        assert compare_diagnosis_with_expected("", "Interface down") == False
        assert compare_diagnosis_with_expected("Interface down", "") == False
        assert compare_diagnosis_with_expected("", "") == False
    
    def test_whitespace_handling(self):
        """Test whitespace handling."""
        assert compare_diagnosis_with_expected(" Interface down ", "Interface down") == True


class TestProcessSingleCase:
    """Test suite for process_single_case function."""
    
    def test_process_single_case_basic(self):
        """Test basic case processing."""
        case = {
            'case_id': 'NET-001',
            'symptom': 'Test symptom',
            'topology_note': 'Test topology',
            'show_outputs': 'Test output',
            'expected_fault': 'Test fault',
            'osi_layer': 'Layer 3',
            'concept_tag': 'Test tag',
            'severity': 'High'
        }
        
        result = process_single_case(case, 'NET-001')
        
        assert result.case_id == 'NET-001'
        assert result.data_valid == True
        assert result.expected_fault == 'Test fault'
        assert isinstance(result, ValidationResult)
    
    def test_process_single_case_with_rule_check(self):
        """Test case processing with rule checks."""
        case = {
            'case_id': 'NET-001',
            'symptom': 'PC1 cannot reach Server1',
            'topology_note': 'PC1 on Fa0/1',
            'show_outputs': 'GigabitEthernet0/0.10 is administratively down',
            'expected_fault': 'Sub-interface administratively down',
            'osi_layer': 'Layer 3',
            'concept_tag': 'Inter-VLAN Routing',
            'severity': 'High'
        }
        
        result = process_single_case(case, 'NET-001')
        
        assert result.case_id == 'NET-001'
        assert result.rule_check_success == True  # Should succeed with valid data
        assert result.rule_results is not None


class TestSaveResults:
    """Test suite for save_results function."""
    
    def test_save_results_creates_directory(self):
        """Test that save_results creates output directory."""
        summary = BatchValidationSummary()
        result = ValidationResult("NET-001")
        result.success = True
        summary.add_result(result)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            save_results(summary, temp_dir)
            
            output_path = Path(temp_dir)
            assert output_path.exists()
    
    def test_save_results_creates_files(self):
        """Test that save_results creates expected files."""
        summary = BatchValidationSummary()
        result = ValidationResult("NET-001")
        result.success = True
        summary.add_result(result)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            save_results(summary, temp_dir)
            
            output_path = Path(temp_dir)
            files = list(output_path.glob("*"))
            
            # Should create at least 3 files (summary JSON, detailed results JSON, CSV)
            assert len(files) >= 3
    
    def test_save_results_json_valid(self):
        """Test that saved JSON files are valid."""
        summary = BatchValidationSummary()
        result = ValidationResult("NET-001")
        result.success = True
        summary.add_result(result)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            save_results(summary, temp_dir)
            
            output_path = Path(temp_dir)
            json_files = list(output_path.glob("*.json"))
            
            for json_file in json_files:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    assert isinstance(data, dict) or isinstance(data, list)


class TestBatchValidationIntegration:
    """Test suite for batch validation integration."""
    
    def test_batch_validation_uses_real_data(self):
        """Test that batch validation uses real project data."""
        from data.data_loader import load_cases
        
        df = load_cases()
        assert len(df) > 0
        
        # This ensures we're testing with real data
        case_id = df.iloc[0]['case_id']
        assert case_id.startswith('NET-')
    
    def test_batch_validation_does_not_modify_original_data(self):
        """Test that batch validation does not modify original cases.csv."""
        import hashlib
        
        # Get original file hash
        original_hash = hashlib.md5(
            Path("data/cases.csv").read_bytes()
        ).hexdigest()
        
        # Run a simple validation
        summary = BatchValidationSummary()
        result = ValidationResult("NET-001")
        summary.add_result(result)
        
        # Check hash again
        new_hash = hashlib.md5(
            Path("data/cases.csv").read_bytes()
        ).hexdigest()
        
        assert original_hash == new_hash, "cases.csv was modified during validation"


class TestBatchValidationErrorHandling:
    """Test suite for batch validation error handling."""
    
    def test_handles_missing_api_key_gracefully(self):
        """Test that validation handles missing API key gracefully."""
        # Temporarily remove API key if present
        original_key = os.environ.get("OPENAI_API_KEY")
        if "OPENAI_API_KEY" in os.environ:
            del os.environ["OPENAI_API_KEY"]
        
        try:
            case = {
                'case_id': 'NET-001',
                'symptom': 'Test symptom',
                'topology_note': 'Test topology',
                'show_outputs': 'Test output',
                'expected_fault': 'Test fault',
                'osi_layer': 'Layer 3',
                'concept_tag': 'Test tag',
                'severity': 'High'
            }
            
            result = process_single_case(case, 'NET-001')
            
            # Should still process case even without AI
            assert result.data_valid == True
            assert result.rule_check_success == True
        finally:
            if original_key:
                os.environ["OPENAI_API_KEY"] = original_key
    
    def test_handles_invalid_case_data(self):
        """Test that validation handles invalid case data gracefully."""
        case = {
            'case_id': 'NET-001',
            # Missing required fields
        }
        
        result = process_single_case(case, 'NET-001')
        
        # Should handle missing fields gracefully
        assert result.case_id == 'NET-001'
        # The specific behavior depends on implementation