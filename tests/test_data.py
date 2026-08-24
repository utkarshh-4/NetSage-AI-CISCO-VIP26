"""Data validation tests for NetSage AI."""

import pytest
import pandas as pd
from pathlib import Path
import tempfile
import os

from data.data_loader import CaseDataLoader, DataValidationError, load_cases


class TestCaseDataLoader:
    """Test suite for CaseDataLoader class."""
    
    def test_load_valid_csv(self):
        """Test loading a valid CSV file."""
        loader = CaseDataLoader("data/cases.csv")
        df = loader.load()
        
        assert df is not None
        assert len(df) > 0
        assert isinstance(df, pd.DataFrame)
    
    def test_file_not_found(self):
        """Test error when CSV file does not exist."""
        loader = CaseDataLoader("data/nonexistent.csv")
        
        with pytest.raises(DataValidationError, match="CSV file not found"):
            loader.load()
    
    def test_required_columns_present(self):
        """Test that all required columns are present."""
        loader = CaseDataLoader("data/cases.csv")
        df = loader.load()
        
        required_columns = [
            "case_id", "symptom", "topology_note", "show_outputs",
            "expected_fault", "osi_layer", "concept_tag", "severity"
        ]
        
        for col in required_columns:
            assert col in df.columns, f"Missing required column: {col}"
    
    def test_no_duplicate_case_ids(self):
        """Test that there are no duplicate case IDs."""
        loader = CaseDataLoader("data/cases.csv")
        df = loader.load()
        
        duplicates = loader.detect_duplicate_case_ids(df)
        assert len(duplicates) == 0, f"Found duplicate case IDs: {duplicates}"
    
    def test_no_missing_values(self):
        """Test that there are no missing values in required columns."""
        loader = CaseDataLoader("data/cases.csv")
        df = loader.load()
        
        missing = loader.detect_missing_values(df)
        assert len(missing) == 0, f"Found missing values: {missing}"
    
    def test_get_case_count(self):
        """Test getting the case count."""
        loader = CaseDataLoader("data/cases.csv")
        df = loader.load()
        
        count = loader.get_case_count()
        assert count == len(df)
        assert count > 0
    
    def test_get_columns(self):
        """Test getting column names."""
        loader = CaseDataLoader("data/cases.csv")
        loader.load()
        
        columns = loader.get_columns()
        assert isinstance(columns, list)
        assert len(columns) > 0
    
    def test_get_case_by_id_valid(self):
        """Test retrieving a case by valid ID."""
        loader = CaseDataLoader("data/cases.csv")
        loader.load()
        
        case = loader.get_case_by_id("NET-001")
        assert case is not None
        assert case["case_id"] == "NET-001"
    
    def test_get_case_by_id_invalid(self):
        """Test error when retrieving non-existent case ID."""
        loader = CaseDataLoader("data/cases.csv")
        loader.load()
        
        with pytest.raises(DataValidationError, match="Case ID not found"):
            loader.get_case_by_id("NONEXISTENT")
    
    def test_csv_not_modified(self):
        """Test that original CSV is not modified during loading."""
        import hashlib
        
        # Get original file hash
        original_hash = hashlib.md5(
            Path("data/cases.csv").read_bytes()
        ).hexdigest()
        
        # Load the file
        loader = CaseDataLoader("data/cases.csv")
        loader.load()
        
        # Check hash again
        new_hash = hashlib.md5(
            Path("data/cases.csv").read_bytes()
        ).hexdigest()
        
        assert original_hash == new_hash, "CSV file was modified during loading"


class TestLoadCasesConvenience:
    """Test suite for load_cases convenience function."""
    
    def test_load_cases_function(self):
        """Test the convenience function loads data correctly."""
        df = load_cases("data/cases.csv")
        
        assert df is not None
        assert len(df) > 0
        assert isinstance(df, pd.DataFrame)


class TestCSVSchemaDetection:
    """Test that actual CSV schema is detected correctly."""
    
    def test_detect_actual_columns(self):
        """Test that actual columns from CSV are detected."""
        loader = CaseDataLoader("data/cases.csv")
        df = loader.load()
        
        actual_columns = list(df.columns)
        expected_columns = [
            "case_id", "symptom", "topology_note", "show_outputs",
            "expected_fault", "osi_layer", "concept_tag", "severity"
        ]
        
        assert actual_columns == expected_columns, \
            f"Column mismatch. Expected: {expected_columns}, Got: {actual_columns}"
    
    def test_case_id_format(self):
        """Test that case IDs follow expected format."""
        loader = CaseDataLoader("data/cases.csv")
        df = loader.load()
        
        for case_id in df["case_id"]:
            assert case_id.startswith("NET-"), \
                f"Case ID {case_id} does not follow NET-XXX format"
    
    def test_severity_values(self):
        """Test that severity values are valid."""
        loader = CaseDataLoader("data/cases.csv")
        df = loader.load()
        
        valid_severities = {"High", "Medium", "Low"}
        for severity in df["severity"]:
            assert severity in valid_severities, \
                f"Invalid severity value: {severity}"


class TestInvalidCSVHandling:
    """Test handling of invalid CSV data."""
    
    def test_missing_column_error(self):
        """Test error when required column is missing."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("case_id,symptom\n")
            f.write("NET-001,Test symptom\n")
            temp_path = f.name
        
        try:
            loader = CaseDataLoader(temp_path)
            with pytest.raises(DataValidationError, match="Missing required columns"):
                loader.load()
        finally:
            os.unlink(temp_path)
    
    def test_duplicate_case_id_error(self):
        """Test error when duplicate case IDs exist."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("case_id,symptom,topology_note,show_outputs,expected_fault,osi_layer,concept_tag,severity\n")
            f.write("NET-001,Symptom1,Note,Output,Fault,Layer3,Tag,High\n")
            f.write("NET-001,Symptom2,Note,Output,Fault,Layer3,Tag,High\n")
            temp_path = f.name
        
        try:
            loader = CaseDataLoader(temp_path)
            with pytest.raises(DataValidationError, match="Duplicate case IDs"):
                loader.load()
        finally:
            os.unlink(temp_path)
    
    def test_missing_value_error(self):
        """Test error when there are missing values."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("case_id,symptom,topology_note,show_outputs,expected_fault,osi_layer,concept_tag,severity\n")
            f.write("NET-001,,Note,Output,Fault,Layer3,Tag,High\n")
            temp_path = f.name
        
        try:
            loader = CaseDataLoader(temp_path)
            with pytest.raises(DataValidationError, match="Missing values"):
                loader.load()
        finally:
            os.unlink(temp_path)
