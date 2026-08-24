"""Analytics metrics for NetSage AI Dashboard."""

import pandas as pd
from typing import Dict, List, Tuple, Any
from data.data_loader import load_cases
from rules.checker import run_all_checks


def calculate_total_cases() -> int:
    """Calculate total number of cases in the dataset."""
    try:
        df = load_cases()
        return len(df)
    except Exception:
        return 0


def calculate_cases_by_issue_type() -> Dict[str, int]:
    """Calculate distribution of cases by issue type (concept_tag)."""
    try:
        df = load_cases()
        if 'concept_tag' in df.columns:
            return df['concept_tag'].value_counts().to_dict()
        return {}
    except Exception:
        return {}


def calculate_cases_by_severity() -> Dict[str, int]:
    """Calculate distribution of cases by severity level."""
    try:
        df = load_cases()
        if 'severity' in df.columns:
            return df['severity'].value_counts().to_dict()
        return {}
    except Exception:
        return {}


def calculate_ai_review_distribution() -> Dict[str, int]:
    """Calculate distribution of AI review decisions (Accepted/Edited/Rejected)."""
    try:
        from review.review_manager import ReviewManager
        review_manager = ReviewManager()
        all_reviews = review_manager.get_all_reviews()
        
        distribution = {"ACCEPT": 0, "EDIT": 0, "REJECT": 0}
        
        for review in all_reviews:
            decision = review.reviewer_decision.value
            if decision in distribution:
                distribution[decision] += 1
        
        return distribution
    except Exception:
        return {"ACCEPT": 0, "EDIT": 0, "REJECT": 0}


def calculate_ai_agreement_rate() -> float:
    """
    Calculate AI-vs-human agreement rate.
    
    Agreement is defined as cases where human reviewer ACCEPTED the AI diagnosis.
    Edited and Rejected cases are considered disagreements.
    
    Returns:
        float: Agreement rate as a percentage (0.0 to 100.0)
    """
    try:
        from review.review_manager import ReviewManager
        review_manager = ReviewManager()
        summary = review_manager.get_summary()
        
        if summary.total_reviews == 0:
            return 0.0
        
        # Agreement rate from review manager
        return summary.agreement_rate * 100  # Convert to percentage
    except Exception:
        return 0.0


def calculate_corrected_diagnoses() -> int:
    """
    Calculate number of corrected AI diagnoses.
    
    This includes both EDIT and REJECT decisions where the human reviewer
    disagreed with the AI diagnosis.
    """
    try:
        from review.review_manager import ReviewManager
        review_manager = ReviewManager()
        summary = review_manager.get_summary()
        
        # Corrected = Edited + Rejected
        return summary.edited_count + summary.rejected_count
    except Exception:
        return 0


def calculate_insufficient_evidence_cases() -> int:
    """
    Calculate number of cases with insufficient evidence from rule checks.
    
    This runs rule checks on all cases and counts how many have insufficient evidence.
    """
    try:
        from rules.checker import run_all_checks
        df = load_cases()
        insufficient_count = 0
        
        for _, case in df.iterrows():
            case_dict = case.to_dict()
            results = run_all_checks(case_dict)
            
            # Count cases where any check returned insufficient evidence
            for result in results:
                if result.status == "INSUFFICIENT_EVIDENCE":
                    insufficient_count += 1
                    break  # Count each case only once
        
        return insufficient_count
    except Exception:
        return 0


def calculate_osi_layer_distribution() -> Dict[str, int]:
    """Calculate distribution of cases by OSI layer."""
    try:
        df = load_cases()
        if 'osi_layer' in df.columns:
            return df['osi_layer'].value_counts().to_dict()
        return {}
    except Exception:
        return {}


def calculate_rule_checker_findings() -> Dict[str, int]:
    """
    Calculate rule checker findings by category.
    
    Returns a dictionary with:
    - 'detected': count of problems detected
    - 'not_detected': count of no issues detected
    - 'insufficient': count of insufficient evidence cases
    """
    try:
        from rules.checker import run_all_checks
        df = load_cases()
        findings = {
            'detected': 0,
            'not_detected': 0,
            'insufficient': 0
        }
        
        for _, case in df.iterrows():
            case_dict = case.to_dict()
            results = run_all_checks(case_dict)
            
            for result in results:
                if result.status == "DETECTED":
                    findings['detected'] += 1
                elif result.status == "NOT_DETECTED":
                    findings['not_detected'] += 1
                elif result.status == "INSUFFICIENT_EVIDENCE":
                    findings['insufficient'] += 1
        
        return findings
    except Exception:
        return {
            'detected': 0,
            'not_detected': 0,
            'insufficient': 0
        }


def get_analytics_summary() -> Dict[str, Any]:
    """
    Get a comprehensive analytics summary.
    
    Returns a dictionary with all key metrics for the dashboard.
    """
    return {
        'total_cases': calculate_total_cases(),
        'cases_by_issue_type': calculate_cases_by_issue_type(),
        'cases_by_severity': calculate_cases_by_severity(),
        'ai_review_distribution': calculate_ai_review_distribution(),
        'ai_agreement_rate': calculate_ai_agreement_rate(),
        'corrected_diagnoses': calculate_corrected_diagnoses(),
        'insufficient_evidence_cases': calculate_insufficient_evidence_cases(),
        'osi_layer_distribution': calculate_osi_layer_distribution(),
        'rule_checker_findings': calculate_rule_checker_findings()
    }


def get_ai_vs_human_comparison() -> List[Dict[str, Any]]:
    """
    Get detailed AI vs human comparison for reviewed cases.
    
    Returns a list of dictionaries showing:
    - case_id
    - ai_diagnosis (root cause)
    - human_decision (ACCEPT/EDIT/REJECT)
    - corrected_diagnosis (if applicable)
    - agreement_status
    """
    try:
        from review.review_manager import ReviewManager
        review_manager = ReviewManager()
        all_reviews = review_manager.get_all_reviews()
        
        comparison = []
        for review in all_reviews:
            comparison.append({
                'case_id': review.case_id,
                'ai_diagnosis': review.ai_diagnosis.get('root_cause', 'N/A') if review.ai_diagnosis else 'N/A',
                'human_decision': review.reviewer_decision.value,
                'corrected_diagnosis': review.corrected_diagnosis.get('root_cause', 'N/A') if review.corrected_diagnosis else None,
                'agreement_status': 'AGREED' if review.ai_human_agreed else 'DISAGREED',
                'timestamp': review.timestamp
            })
        
        return comparison
    except Exception:
        return []