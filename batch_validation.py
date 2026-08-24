"""NetSage AI - Full Dataset Validation Batch Script.

This script processes all cases from the dataset and runs the complete pipeline:
1. Load and validate case data
2. Run deterministic rule checks
3. Run AI diagnosis (if API available)
4. Validate AI schema
5. Compare AI diagnosis with expected fault
6. Record all outputs and metadata
7. Generate comprehensive summary
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import json
import csv
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

# Set UTF-8 encoding for output
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add parent directory to Python path
parent_dir = Path(__file__).parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from data.data_loader import load_cases, CaseDataLoader, DataValidationError
from rules.checker import run_all_checks
from ai.diagnose import diagnose_case
from ai.schemas import DiagnosisResponse, DiagnosisError
from review.review_manager import ReviewManager, ReviewDecision


class ValidationResult:
    """Stores validation result for a single case."""
    
    def __init__(self, case_id: str):
        self.case_id = case_id
        self.success = False
        self.data_valid = False
        self.rule_check_success = False
        self.ai_diagnosis_success = False
        self.ai_schema_valid = False
        self.expected_fault = None
        self.ai_root_cause = None
        self.ai_agreement = False
        self.insufficient_evidence = False
        self.error_message = None
        self.rule_results = None
        self.ai_diagnosis = None
        self.ai_error = None
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            'case_id': self.case_id,
            'success': self.success,
            'data_valid': self.data_valid,
            'rule_check_success': self.rule_check_success,
            'ai_diagnosis_success': self.ai_diagnosis_success,
            'ai_schema_valid': self.ai_schema_valid,
            'expected_fault': self.expected_fault,
            'ai_root_cause': self.ai_root_cause,
            'ai_agreement': self.ai_agreement,
            'insufficient_evidence': self.insufficient_evidence,
            'error_message': self.error_message,
            'rule_results': self.rule_results,
            'ai_diagnosis': self.ai_diagnosis,
            'ai_error': self.ai_error,
            'timestamp': self.timestamp
        }


class BatchValidationSummary:
    """Stores summary statistics for batch validation."""
    
    def __init__(self):
        self.total_cases = 0
        self.successfully_processed = 0
        self.rule_checker_failures = 0
        self.ai_failures = 0
        self.schema_failures = 0
        self.insufficient_evidence_cases = 0
        self.ai_expected_agreement = 0
        self.human_accepted = 0
        self.human_edited = 0
        self.human_rejected = 0
        self.validation_results: List[ValidationResult] = []
    
    def add_result(self, result: ValidationResult):
        """Add a validation result and update statistics."""
        self.validation_results.append(result)
        self.total_cases += 1
        
        if result.success:
            self.successfully_processed += 1
        
        if not result.rule_check_success:
            self.rule_checker_failures += 1
        
        if not result.ai_diagnosis_success:
            self.ai_failures += 1
        
        if not result.ai_schema_valid and result.ai_diagnosis_success:
            self.schema_failures += 1
        
        if result.insufficient_evidence:
            self.insufficient_evidence_cases += 1
        
        if result.ai_agreement:
            self.ai_expected_agreement += 1
    
    def add_human_review(self, decision: str):
        """Add human review decision to statistics."""
        if decision == "ACCEPT":
            self.human_accepted += 1
        elif decision == "EDIT":
            self.human_edited += 1
        elif decision == "REJECT":
            self.human_rejected += 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            'total_cases': self.total_cases,
            'successfully_processed': self.successfully_processed,
            'rule_checker_failures': self.rule_checker_failures,
            'ai_failures': self.ai_failures,
            'schema_failures': self.schema_failures,
            'insufficient_evidence_cases': self.insufficient_evidence_cases,
            'ai_expected_agreement': self.ai_expected_agreement,
            'human_accepted': self.human_accepted,
            'human_edited': self.human_edited,
            'human_rejected': self.human_rejected,
            'success_rate': self.successfully_processed / self.total_cases if self.total_cases > 0 else 0,
            'ai_expected_agreement_rate': self.ai_expected_agreement / self.total_cases if self.total_cases > 0 else 0
        }


def process_single_case(case: Dict[str, str], case_id: str) -> ValidationResult:
    """Process a single case through the complete pipeline."""
    result = ValidationResult(case_id)
    
    try:
        # Step 1: Validate case data
        result.data_valid = True
        result.expected_fault = case.get('expected_fault', 'N/A')
        
        # Step 2: Run deterministic rules
        try:
            rule_results = run_all_checks(case)
            result.rule_check_success = True
            result.rule_results = [r.to_dict() for r in rule_results]
            
            # Check for insufficient evidence
            for r in rule_results:
                if r.status == "INSUFFICIENT_EVIDENCE":
                    result.insufficient_evidence = True
                    break
        except Exception as e:
            result.rule_check_success = False
            result.error_message = f"Rule check failed: {str(e)}"
        
        # Step 3: Run AI diagnosis (if API available and not skipped)
        skip_ai = os.getenv("SKIP_AI", "false").lower() == "true"
        
        if not skip_ai:
            try:
                # Convert rule results to dict format
                rule_results_dict = None
                if result.rule_results:
                    rule_results_dict = {
                        r['check_name']: r for r in result.rule_results
                    }
                
                ai_result = diagnose_case(case, rule_results=rule_results_dict)
                
                # Check if result is a diagnosis or error
                if hasattr(ai_result, 'root_cause'):
                    # Valid diagnosis
                    result.ai_diagnosis_success = True
                    result.ai_schema_valid = True
                    result.ai_diagnosis = ai_result.model_dump()
                    result.ai_root_cause = ai_result.root_cause
                    
                    # Step 4: Compare with expected fault
                    result.ai_agreement = compare_diagnosis_with_expected(
                        ai_result.root_cause, 
                        result.expected_fault
                    )
                else:
                    # Error response
                    result.ai_diagnosis_success = False
                    result.ai_error = ai_result.model_dump()
                    result.error_message = f"AI diagnosis error: {ai_result.message}"
                    
            except Exception as e:
                result.ai_diagnosis_success = False
                result.ai_error = str(e)
                result.error_message = f"AI diagnosis failed: {str(e)}"
        else:
            # AI skipped - mark as not attempted
            result.ai_diagnosis_success = False
            result.ai_error = "AI diagnosis skipped (SKIP_AI=true)"
        
        # Step 5: Mark as successful if core processing completed
        if result.data_valid and result.rule_check_success:
            result.success = True
            
    except Exception as e:
        result.success = False
        result.error_message = f"Case processing failed: {str(e)}"
    
    return result


def compare_diagnosis_with_expected(ai_root_cause: str, expected_fault: str) -> bool:
    """Compare AI diagnosis with expected fault.
    
    This is a simple string comparison. In a real system, you might want
    more sophisticated comparison logic (fuzzy matching, semantic similarity, etc.)
    """
    if not ai_root_cause or not expected_fault:
        return False
    
    # Normalize strings for comparison
    ai_normalized = ai_root_cause.lower().strip()
    expected_normalized = expected_fault.lower().strip()
    
    # Check for exact match or containment
    return ai_normalized == expected_normalized or ai_normalized in expected_normalized or expected_normalized in ai_normalized


def run_batch_validation() -> BatchValidationSummary:
    """Run batch validation on all cases."""
    print("Starting NetSage AI Batch Validation...")
    print("=" * 60)
    
    summary = BatchValidationSummary()
    
    try:
        # Load all cases
        print("Loading cases from dataset...")
        df = load_cases()
        print(f"Loaded {len(df)} cases")
        
        # Process each case
        for index, row in df.iterrows():
            case_id = row['case_id']
            case_dict = row.to_dict()
            
            print(f"Processing case {index + 1}/{len(df)}: {case_id}")
            
            result = process_single_case(case_dict, case_id)
            summary.add_result(result)
            
            status = "SUCCESS" if result.success else "FAILED"
            print(f"  {status} - AI Agreement: {result.ai_agreement}")
            
            if result.error_message:
                print(f"  Error: {result.error_message}")
        
        print("\n" + "=" * 60)
        print("Batch Validation Complete")
        print("=" * 60)
        
    except Exception as e:
        print(f"Batch validation failed: {str(e)}")
        summary.error_message = str(e)
    
    return summary


def save_results(summary: BatchValidationSummary, output_dir: str = "validation_results"):
    """Save validation results to files."""
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save summary
    summary_file = output_path / f"summary_{timestamp}.json"
    with open(summary_file, 'w') as f:
        json.dump(summary.to_dict(), f, indent=2)
    print(f"Summary saved to: {summary_file}")
    
    # Save detailed results
    results_file = output_path / f"detailed_results_{timestamp}.json"
    detailed_results = [r.to_dict() for r in summary.validation_results]
    with open(results_file, 'w') as f:
        json.dump(detailed_results, f, indent=2)
    print(f"Detailed results saved to: {results_file}")
    
    # Save CSV summary
    csv_file = output_path / f"summary_{timestamp}.csv"
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Case ID', 'Success', 'Data Valid', 'Rule Check Success', 
                        'AI Success', 'Schema Valid', 'AI Agreement', 'Insufficient Evidence',
                        'Expected Fault', 'AI Root Cause', 'Error Message'])
        
        for result in summary.validation_results:
            writer.writerow([
                result.case_id,
                result.success,
                result.data_valid,
                result.rule_check_success,
                result.ai_diagnosis_success,
                result.ai_schema_valid,
                result.ai_agreement,
                result.insufficient_evidence,
                result.expected_fault,
                result.ai_root_cause,
                result.error_message
            ])
    print(f"CSV summary saved to: {csv_file}")


def print_summary(summary: BatchValidationSummary):
    """Print a formatted summary to console."""
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    
    print(f"Total Cases: {summary.total_cases}")
    print(f"Successfully Processed: {summary.successfully_processed}")
    print(f"Success Rate: {summary.to_dict()['success_rate']:.1%}")
    print()
    print(f"Rule Checker Failures: {summary.rule_checker_failures}")
    print(f"AI Failures: {summary.ai_failures}")
    print(f"Schema Failures: {summary.schema_failures}")
    print(f"Insufficient Evidence Cases: {summary.insufficient_evidence_cases}")
    print()
    print(f"AI/Expected Agreement: {summary.ai_expected_agreement}/{summary.total_cases}")
    print(f"AI/Expected Agreement Rate: {summary.to_dict()['ai_expected_agreement_rate']:.1%}")
    print()
    print(f"Human Accepted: {summary.human_accepted}")
    print(f"Human Edited: {summary.human_edited}")
    print(f"Human Rejected: {summary.human_rejected}")
    print("=" * 60)


def main():
    """Main entry point for batch validation."""
    print("NetSage AI - Full Dataset Validation")
    print("=" * 60)
    
    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    skip_ai = os.getenv("SKIP_AI", "false").lower() == "true"
    
    if skip_ai:
        print("AI diagnosis skipped (SKIP_AI=true)")
        print("Running validation with rule-based analysis only")
    elif api_key:
        print("OpenAI API key found - AI diagnosis will be attempted")
    else:
        print("No OpenAI API key found - AI diagnosis will be skipped")
        print("Set OPENAI_API_KEY environment variable to enable AI diagnosis")
        print("Or set SKIP_AI=true to skip AI calls explicitly")
    
    print()
    
    # Temporarily remove API key if skipping AI
    if skip_ai and api_key:
        original_key = os.environ["OPENAI_API_KEY"]
        del os.environ["OPENAI_API_KEY"]
    
    try:
        # Run batch validation
        summary = run_batch_validation()
        
        # Print summary
        print_summary(summary)
        
        # Save results
        save_results(summary)
        
        print("\nValidation complete!")
        print("Results have been saved to the 'validation_results' directory")
    finally:
        # Restore API key if it was removed
        if skip_ai and api_key:
            os.environ["OPENAI_API_KEY"] = original_key


if __name__ == "__main__":
    main()