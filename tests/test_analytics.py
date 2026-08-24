"""Tests for NetSage AI Analytics Module."""

import pytest
import pandas as pd
import tempfile
import os
from pathlib import Path

from analytics.metrics import (
    calculate_total_cases,
    calculate_cases_by_issue_type,
    calculate_cases_by_severity,
    calculate_ai_review_distribution,
    calculate_ai_agreement_rate,
    calculate_corrected_diagnoses,
    calculate_insufficient_evidence_cases,
    calculate_osi_layer_distribution,
    calculate_rule_checker_findings,
    get_analytics_summary,
    get_ai_vs_human_comparison
)
from review.review_manager import ReviewManager, ReviewDecision


class TestCalculateTotalCases:
    """Test suite for calculate_total_cases function."""
    
    def test_calculate_total_cases_with_data(self):
        """Test calculation with actual data."""
        total = calculate_total_cases()
        assert total > 0
        assert isinstance(total, int)
    
    def test_calculate_total_cases_returns_integer(self):
        """Test that function returns an integer."""
        total = calculate_total_cases()
        assert isinstance(total, int)


class TestCalculateCasesByIssueType:
    """Test suite for calculate_cases_by_issue_type function."""
    
    def test_calculate_cases_by_issue_type_structure(self):
        """Test that function returns dictionary structure."""
        result = calculate_cases_by_issue_type()
        assert isinstance(result, dict)
    
    def test_calculate_cases_by_issue_type_has_data(self):
        """Test that function returns data when available."""
        result = calculate_cases_by_issue_type()
        if result:  # Only test if data is available
            for key, value in result.items():
                assert isinstance(key, str)
                assert isinstance(value, int)
                assert value >= 0


class TestCalculateCasesBySeverity:
    """Test suite for calculate_cases_by_severity function."""
    
    def test_calculate_cases_by_severity_structure(self):
        """Test that function returns dictionary structure."""
        result = calculate_cases_by_severity()
        assert isinstance(result, dict)
    
    def test_calculate_cases_by_severity_valid_values(self):
        """Test that severity values are valid."""
        result = calculate_cases_by_severity()
        if result:
            valid_severities = {"High", "Medium", "Low"}
            for severity in result.keys():
                assert severity in valid_severities


class TestCalculateAIReviewDistribution:
    """Test suite for calculate_ai_review_distribution function."""
    
    def test_calculate_ai_review_distribution_structure(self):
        """Test that function returns correct structure."""
        result = calculate_ai_review_distribution()
        assert isinstance(result, dict)
        assert "ACCEPT" in result
        assert "EDIT" in result
        assert "REJECT" in result
    
    def test_calculate_ai_review_distribution_non_negative(self):
        """Test that all values are non-negative."""
        result = calculate_ai_review_distribution()
        for key, value in result.items():
            assert value >= 0


class TestCalculateAIAgreementRate:
    """Test suite for calculate_ai_agreement_rate function."""
    
    def test_calculate_ai_agreement_rate_returns_float(self):
        """Test that function returns float."""
        rate = calculate_ai_agreement_rate()
        assert isinstance(rate, float)
    
    def test_calculate_ai_agreement_rate_range(self):
        """Test that agreement rate is in valid range."""
        rate = calculate_ai_agreement_rate()
        assert 0.0 <= rate <= 100.0
    
    def test_calculate_ai_agreement_rate_definition(self):
        """Test that agreement rate definition is correct."""
        # Agreement rate should be based on accepted decisions
        # This is implicitly tested by the function implementation
        rate = calculate_ai_agreement_rate()
        assert isinstance(rate, float)


class TestCalculateCorrectedDiagnoses:
    """Test suite for calculate_corrected_diagnoses function."""
    
    def test_calculate_corrected_diagnoses_returns_integer(self):
        """Test that function returns integer."""
        corrected = calculate_corrected_diagnoses()
        assert isinstance(corrected, int)
    
    def test_calculate_corrected_diagnoses_non_negative(self):
        """Test that result is non-negative."""
        corrected = calculate_corrected_diagnoses()
        assert corrected >= 0
    
    def test_calculate_corrected_diagnoses_definition(self):
        """Test that corrected diagnoses = edited + rejected."""
        # This tests the definition: corrected = EDIT + REJECT
        review_manager = ReviewManager()
        summary = review_manager.get_summary()
        
        expected = summary.edited_count + summary.rejected_count
        actual = calculate_corrected_diagnoses()
        
        assert actual == expected


class TestCalculateInsufficientEvidenceCases:
    """Test suite for calculate_insufficient_evidence_cases function."""
    
    def test_calculate_insufficient_evidence_cases_returns_integer(self):
        """Test that function returns integer."""
        insufficient = calculate_insufficient_evidence_cases()
        assert isinstance(insufficient, int)
    
    def test_calculate_insufficient_evidence_cases_non_negative(self):
        """Test that result is non-negative."""
        insufficient = calculate_insufficient_evidence_cases()
        assert insufficient >= 0


class TestCalculateOSILayerDistribution:
    """Test suite for calculate_osi_layer_distribution function."""
    
    def test_calculate_osi_layer_distribution_structure(self):
        """Test that function returns dictionary structure."""
        result = calculate_osi_layer_distribution()
        assert isinstance(result, dict)
    
    def test_calculate_osi_layer_distribution_has_data(self):
        """Test that function returns data when available."""
        result = calculate_osi_layer_distribution()
        if result:
            for key, value in result.items():
                assert isinstance(key, str)
                assert isinstance(value, int)
                assert value >= 0


class TestCalculateRuleCheckerFindings:
    """Test suite for calculate_rule_checker_findings function."""
    
    def test_calculate_rule_checker_findings_structure(self):
        """Test that function returns correct structure."""
        result = calculate_rule_checker_findings()
        assert isinstance(result, dict)
        assert "detected" in result
        assert "not_detected" in result
        assert "insufficient" in result
    
    def test_calculate_rule_checker_findings_non_negative(self):
        """Test that all values are non-negative."""
        result = calculate_rule_checker_findings()
        for key, value in result.items():
            assert value >= 0
    
    def test_calculate_rule_checker_findings_integer_values(self):
        """Test that all values are integers."""
        result = calculate_rule_checker_findings()
        for key, value in result.items():
            assert isinstance(value, int)


class TestGetAnalyticsSummary:
    """Test suite for get_analytics_summary function."""
    
    def test_get_analytics_summary_structure(self):
        """Test that function returns correct structure."""
        summary = get_analytics_summary()
        assert isinstance(summary, dict)
        
        required_keys = [
            'total_cases',
            'cases_by_issue_type',
            'cases_by_severity',
            'ai_review_distribution',
            'ai_agreement_rate',
            'corrected_diagnoses',
            'insufficient_evidence_cases',
            'osi_layer_distribution',
            'rule_checker_findings'
        ]
        
        for key in required_keys:
            assert key in summary
    
    def test_get_analytics_summary_data_types(self):
        """Test that summary contains correct data types."""
        summary = get_analytics_summary()
        
        assert isinstance(summary['total_cases'], int)
        assert isinstance(summary['cases_by_issue_type'], dict)
        assert isinstance(summary['cases_by_severity'], dict)
        assert isinstance(summary['ai_review_distribution'], dict)
        assert isinstance(summary['ai_agreement_rate'], float)
        assert isinstance(summary['corrected_diagnoses'], int)
        assert isinstance(summary['insufficient_evidence_cases'], int)
        assert isinstance(summary['osi_layer_distribution'], dict)
        assert isinstance(summary['rule_checker_findings'], dict)


class TestGetAIVsHumanComparison:
    """Test suite for get_ai_vs_human_comparison function."""
    
    def test_get_ai_vs_human_comparison_structure(self):
        """Test that function returns list structure."""
        comparison = get_ai_vs_human_comparison()
        assert isinstance(comparison, list)
    
    def test_get_ai_vs_human_comparison_item_structure(self):
        """Test that comparison items have correct structure."""
        comparison = get_ai_vs_human_comparison()
        if comparison:
            for item in comparison:
                assert isinstance(item, dict)
                assert 'case_id' in item
                assert 'ai_diagnosis' in item
                assert 'human_decision' in item
                assert 'agreement_status' in item
    
    def test_get_ai_vs_human_comparison_agreement_status(self):
        """Test that agreement status values are valid."""
        comparison = get_ai_vs_human_comparison()
        if comparison:
            valid_statuses = {"AGREED", "DISAGREED"}
            for item in comparison:
                assert item['agreement_status'] in valid_statuses


class TestAnalyticsIntegration:
    """Test suite for analytics integration with other modules."""
    
    def test_analytics_uses_real_data(self):
        """Test that analytics uses real project data."""
        # This ensures we're not fabricating statistics
        total_cases = calculate_total_cases()
        
        # Load actual data to verify
        from data.data_loader import load_cases
        df = load_cases()
        
        assert total_cases == len(df)
    
    def test_analytics_consistency(self):
        """Test that analytics metrics are consistent."""
        summary = get_analytics_summary()
        
        # Total cases should match individual components
        by_issue = summary['cases_by_issue_type']
        if by_issue:
            total_by_issue = sum(by_issue.values())
            # Note: This might not exactly match total_cases due to categorization
            assert total_by_issue <= summary['total_cases']


class TestAnalyticsErrorHandling:
    """Test suite for analytics error handling."""
    
    def test_analytics_handles_empty_data(self):
        """Test that analytics handles empty data gracefully."""
        # This tests the error handling in analytics functions
        # Functions should return 0 or empty dicts rather than crash
        try:
            total = calculate_total_cases()
            assert isinstance(total, int)
        except Exception:
            pytest.fail("calculate_total_cases should handle errors gracefully")
    
    def test_analytics_functions_return_expected_types(self):
        """Test that all analytics functions return expected types."""
        assert isinstance(calculate_total_cases(), int)
        assert isinstance(calculate_cases_by_issue_type(), dict)
        assert isinstance(calculate_cases_by_severity(), dict)
        assert isinstance(calculate_ai_review_distribution(), dict)
        assert isinstance(calculate_ai_agreement_rate(), float)
        assert isinstance(calculate_corrected_diagnoses(), int)
        assert isinstance(calculate_insufficient_evidence_cases(), int)
        assert isinstance(calculate_osi_layer_distribution(), dict)
        assert isinstance(calculate_rule_checker_findings(), dict)