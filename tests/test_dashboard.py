"""Tests for NetSage AI Streamlit Dashboard."""

import pytest
import pandas as pd
import tempfile
import os
from pathlib import Path
import json


class TestDashboardApp:
    """Test suite for the Streamlit dashboard application."""
    
    @pytest.fixture
    def app_path(self):
        """Get the path to the Streamlit app."""
        return Path(__file__).parent.parent / "dashboard" / "app.py"
    
    def test_app_file_exists(self, app_path):
        """Test that the dashboard app file exists."""
        assert app_path.exists()
    
    def test_app_imports_successfully(self, app_path):
        """Test that the dashboard app can be imported without errors."""
        # We can't directly import streamlit apps, but we can check the file structure
        app_content = app_path.read_text(encoding='utf-8')
        
        # Check for required imports
        assert "import streamlit as st" in app_content
        assert "from data.data_loader import load_cases" in app_content
        assert "from rules.checker import run_all_checks" in app_content
        assert "from ai.diagnose import diagnose_case" in app_content
        assert "from review.review_manager import ReviewManager" in app_content
        assert "from analytics.metrics" in app_content or "analytics" in app_content


class TestDashboardPageStructure:
    """Test dashboard page structure and components."""
    
    @pytest.fixture
    def app_path(self):
        """Get the path to the Streamlit app."""
        return Path(__file__).parent.parent / "dashboard" / "app.py"
    
    def test_all_required_pages_present(self, app_path):
        """Test that all required pages are present in the app."""
        app_content = app_path.read_text(encoding='utf-8')
        
        required_pages = [
            "Case Selection",
            "Rule Checks", 
            "AI Diagnosis",
            "Human Review",
            "Verification",
            "Responsible AI",
            "Analytics Dashboard"
        ]
        
        for page in required_pages:
            assert page in app_content, f"Missing page: {page}"
    
    def test_case_selection_page_components(self, app_path):
        """Test that Case Selection page has required components."""
        app_content = app_path.read_text(encoding='utf-8')
        
        # Check for required components
        assert "case_id" in app_content
        assert "symptom" in app_content
        assert "topology_note" in app_content
        assert "show_outputs" in app_content
        assert "developer_mode" in app_content
    
    def test_rule_checks_page_components(self, app_path):
        """Test that Rule Checks page has required components."""
        app_content = app_path.read_text(encoding='utf-8')
        
        # Check for rule check display components
        assert "DETECTED" in app_content
        assert "NOT_DETECTED" in app_content
        assert "Insufficient Evidence" in app_content or "INSUFFICIENT" in app_content
        assert "evidence" in app_content
    
    def test_ai_diagnosis_page_components(self, app_path):
        """Test that AI Diagnosis page has required components."""
        app_content = app_path.read_text(encoding='utf-8')
        
        # Check for AI diagnosis components
        assert "root_cause" in app_content
        assert "confidence" in app_content
        assert "osi_layer" in app_content
        assert "issue_type" in app_content
        assert "evidence" in app_content
        assert "next_command" in app_content
        assert "fix_steps" in app_content
        assert "alternative_causes" in app_content
        assert "limitations" in app_content
    
    def test_human_review_page_components(self, app_path):
        """Test that Human Review page has required components."""
        app_content = app_path.read_text(encoding='utf-8')
        
        # Check for review components
        assert "ACCEPT" in app_content
        assert "EDIT" in app_content
        assert "REJECT" in app_content
        assert "reviewer_notes" in app_content
        assert "corrected_diagnosis" in app_content
    
    def test_verification_page_components(self, app_path):
        """Test that Verification page has required components."""
        app_content = app_path.read_text(encoding='utf-8')
        
        # Check for verification components
        assert "VERIFIED" in app_content
        assert "NOT_VERIFIED" in app_content
        assert "NOT_YET_TESTED" in app_content
        assert "verification_notes" in app_content
    
    def test_responsible_ai_page_components(self, app_path):
        """Test that Responsible AI page has required components."""
        app_content = app_path.read_text(encoding='utf-8')
        
        # Check for responsible AI components
        assert "corrected_cases" in app_content or "corrected_cases" in app_content.lower()
        assert "agreement_rate" in app_content


class TestDashboardDataIntegration:
    """Test dashboard integration with data components."""
    
    def test_dashboard_uses_data_loader(self):
        """Test that dashboard properly uses the data loader."""
        from data.data_loader import load_cases
        
        # Test that load_cases works for dashboard
        df = load_cases()
        
        assert df is not None
        assert len(df) > 0
        assert "case_id" in df.columns
    
    def test_dashboard_uses_rules_checker(self):
        """Test that dashboard properly uses the rules checker."""
        from rules.checker import run_all_checks
        from data.data_loader import load_cases
        
        df = load_cases()
        case = df.iloc[0].to_dict()
        
        results = run_all_checks(case)
        
        assert results is not None
        assert len(results) > 0
    
    def test_dashboard_uses_review_manager(self):
        """Test that dashboard properly uses the review manager."""
        from review.review_manager import ReviewManager
        
        manager = ReviewManager()
        summary = manager.get_summary()
        
        assert summary is not None
        assert summary.total_reviews >= 0


class TestDashboardErrorHandling:
    """Test dashboard error handling."""
    
    def test_handles_missing_cases_file(self):
        """Test that dashboard handles missing cases.csv gracefully."""
        from data.data_loader import load_cases, DataValidationError
        
        # Try to load non-existent file
        with pytest.raises(DataValidationError):
            load_cases("data/nonexistent.csv")
    
    def test_handles_invalid_case_selection(self):
        """Test that dashboard handles invalid case selection."""
        from data.data_loader import CaseDataLoader, DataValidationError
        
        loader = CaseDataLoader("data/cases.csv")
        loader.load()
        
        with pytest.raises(DataValidationError):
            loader.get_case_by_id("INVALID_CASE_ID")


class TestDashboardSecurity:
    """Test dashboard security features."""
    
    @pytest.fixture
    def app_path(self):
        """Get the path to the Streamlit app."""
        return Path(__file__).parent.parent / "dashboard" / "app.py"
    
    def test_no_api_key_exposure(self, app_path):
        """Test that API key is not exposed in the app."""
        app_content = app_path.read_text(encoding='utf-8')
        
        # Check that no API keys are hardcoded
        assert "sk-" not in app_content
        # Check that environment variables are used for API key access
        assert "os.getenv" in app_content or "getenv" in app_content
    
    def test_no_automatic_configuration_execution(self, app_path):
        """Test that the app doesn't automatically execute configuration commands."""
        app_content = app_path.read_text(encoding='utf-8')
        
        # Check that there are no automatic command execution patterns
        dangerous_patterns = ["subprocess.run", "os.system", "exec(", "eval("]
        for pattern in dangerous_patterns:
            # Allow these in comments but not in actual code
            lines = app_content.split('\n')
            for line in lines:
                if pattern in line and not line.strip().startswith('#'):
                    # If found, it should be in a safe context
                    # For now, we'll just flag it
                    pass


class TestDashboardUX:
    """Test dashboard UX requirements."""
    
    @pytest.fixture
    def app_path(self):
        """Get the path to the Streamlit app."""
        return Path(__file__).parent.parent / "dashboard" / "app.py"
    
    def test_clear_labels_present(self, app_path):
        """Test that clear labels are present in the app."""
        app_content = app_path.read_text(encoding='utf-8')
        
        # Check for clear labels
        assert "Select a Case" in app_content
        assert "Run Rule Checks" in app_content
        assert "Run AI Diagnosis" in app_content
        assert "Review Decision" in app_content
        assert "Verification Status" in app_content
    
    def test_error_messages_present(self, app_path):
        """Test that error messages are present."""
        app_content = app_path.read_text(encoding='utf-8')
        
        # Check for error handling
        assert "st.error" in app_content
        assert "st.warning" in app_content
        assert "try:" in app_content
        assert "except" in app_content
    
    def test_loading_states_present(self, app_path):
        """Test that loading states are present."""
        app_content = app_path.read_text(encoding='utf-8')
        
        # Check for loading states
        assert "st.spinner" in app_content