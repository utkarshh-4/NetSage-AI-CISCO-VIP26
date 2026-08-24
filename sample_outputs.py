"""Sample outputs demonstrating the deterministic rule checker."""

from data.data_loader import load_cases
from rules.checker import run_all_checks, summarize_results
import json


def print_sample_outputs():
    """Generate and print sample outputs for a few cases."""
    
    # Load the cases
    df = load_cases()
    
    # Select a few representative cases
    sample_case_ids = ["NET-001", "NET-009", "NET-023"]
    
    for case_id in sample_case_ids:
        case_row = df[df["case_id"] == case_id].iloc[0]
        case = case_row.to_dict()
        
        print(f"\n{'='*80}")
        print(f"CASE: {case_id}")
        print(f"{'='*80}")
        print(f"Symptom: {case['symptom']}")
        print(f"Expected Fault: {case['expected_fault']}")
        print(f"Severity: {case['severity']}")
        print(f"\n{'-'*80}")
        print("DETERMINISTIC RULE CHECK RESULTS:")
        print(f"{'-'*80}")
        
        results = run_all_checks(case)
        
        for result in results:
            print(f"\n{result.check_name.upper()}")
            print(f"  Status: {result.status}")
            print(f"  Severity: {result.severity}")
            print(f"  Confidence: {result.confidence}")
            print(f"  Message: {result.message}")
            if result.evidence:
                print(f"  Evidence:")
                for ev in result.evidence:
                    print(f"    - {ev}")
        
        summary = summarize_results(results)
        print(f"\n{'-'*80}")
        print("SUMMARY:")
        print(f"  Total checks: {summary['total_checks']}")
        print(f"  Detected: {summary['detected']}")
        print(f"  Not detected: {summary['not_detected']}")
        print(f"  Insufficient evidence: {summary['insufficient_evidence']}")
        print(f"  Errors: {summary['errors']}")


if __name__ == "__main__":
    print_sample_outputs()
