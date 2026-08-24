"""Data loader module for loading and validating cases.csv."""

import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataValidationError(Exception):
    """Custom exception for data validation errors."""
    pass


class CaseDataLoader:
    """Loads and validates network troubleshooting cases from CSV."""
    
    def __init__(self, csv_path: str = "data/cases.csv"):
        """
        Initialize the data loader.
        
        Args:
            csv_path: Path to the cases.csv file
        """
        self.csv_path = Path(csv_path)
        self.df: pd.DataFrame = None
        self.required_columns = [
            "case_id", "symptom", "topology_note", "show_outputs",
            "expected_fault", "osi_layer", "concept_tag", "severity"
        ]
    
    def validate_file_exists(self) -> None:
        """Validate that the CSV file exists."""
        if not self.csv_path.exists():
            raise DataValidationError(
                f"CSV file not found at: {self.csv_path.absolute()}"
            )
        logger.info(f"File exists: {self.csv_path.absolute()}")
    
    def validate_columns(self, df: pd.DataFrame) -> None:
        """
        Validate that required columns exist in the DataFrame.
        
        Args:
            df: DataFrame to validate
            
        Raises:
            DataValidationError: If required columns are missing
        """
        missing_columns = set(self.required_columns) - set(df.columns)
        if missing_columns:
            raise DataValidationError(
                f"Missing required columns: {missing_columns}. "
                f"Found columns: {list(df.columns)}"
            )
        logger.info(f"All required columns present: {self.required_columns}")
    
    def detect_duplicate_case_ids(self, df: pd.DataFrame) -> List[str]:
        """
        Detect duplicate case IDs.
        
        Args:
            df: DataFrame to check
            
        Returns:
            List of duplicate case IDs
        """
        duplicates = df[df.duplicated(subset=["case_id"], keep=False)]["case_id"].tolist()
        if duplicates:
            logger.warning(f"Found duplicate case IDs: {set(duplicates)}")
        return list(set(duplicates))
    
    def detect_missing_values(self, df: pd.DataFrame) -> Dict[str, int]:
        """
        Detect missing values in each column.
        
        Args:
            df: DataFrame to check
            
        Returns:
            Dictionary mapping column names to count of missing values
        """
        missing_counts = df.isnull().sum()
        missing_dict = missing_counts[missing_counts > 0].to_dict()
        
        if missing_dict:
            logger.warning(f"Found missing values: {missing_dict}")
        else:
            logger.info("No missing values found")
        
        return missing_dict
    
    def load(self) -> pd.DataFrame:
        """
        Load and validate the cases CSV file.
        
        Returns:
            Validated DataFrame with case data
            
        Raises:
            DataValidationError: If validation fails
        """
        # Validate file exists
        self.validate_file_exists()
        
        # Load CSV
        try:
            self.df = pd.read_csv(self.csv_path)
            logger.info(f"Loaded {len(self.df)} rows from CSV")
        except Exception as e:
            raise DataValidationError(f"Failed to read CSV: {e}")
        
        # Validate columns
        self.validate_columns(self.df)
        
        # Check for duplicates
        duplicates = self.detect_duplicate_case_ids(self.df)
        if duplicates:
            raise DataValidationError(
                f"Duplicate case IDs found: {duplicates}"
            )
        
        # Check for missing values
        missing = self.detect_missing_values(self.df)
        if missing:
            raise DataValidationError(
                f"Missing values found in columns: {missing}"
            )
        
        logger.info("Data validation passed successfully")
        return self.df
    
    def get_case_count(self) -> int:
        """Return the number of cases in the dataset."""
        if self.df is None:
            raise DataValidationError("Data not loaded. Call load() first.")
        return len(self.df)
    
    def get_columns(self) -> List[str]:
        """Return the column names in the dataset."""
        if self.df is None:
            raise DataValidationError("Data not loaded. Call load() first.")
        return list(self.df.columns)
    
    def get_case_by_id(self, case_id: str) -> pd.Series:
        """
        Get a specific case by its ID.
        
        Args:
            case_id: The case ID to retrieve
            
        Returns:
            Series containing the case data
            
        Raises:
            DataValidationError: If case ID not found
        """
        if self.df is None:
            raise DataValidationError("Data not loaded. Call load() first.")
        
        case = self.df[self.df["case_id"] == case_id]
        if case.empty:
            raise DataValidationError(f"Case ID not found: {case_id}")
        
        return case.iloc[0]


def load_cases(csv_path: str = "data/cases.csv") -> pd.DataFrame:
    """
    Convenience function to load and validate cases.
    
    Args:
        csv_path: Path to the cases.csv file
        
    Returns:
        Validated DataFrame with case data
    """
    loader = CaseDataLoader(csv_path)
    return loader.load()
