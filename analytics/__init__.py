"""NetSage AI Analytics Module."""

from analytics.metrics import (
    calculate_total_cases,
    calculate_cases_by_issue_type,
    calculate_cases_by_severity,
    calculate_ai_review_distribution,
    calculate_ai_agreement_rate,
    calculate_corrected_diagnoses,
    calculate_insufficient_evidence_cases,
    calculate_osi_layer_distribution,
    calculate_rule_checker_findings
)

__all__ = [
    'calculate_total_cases',
    'calculate_cases_by_issue_type',
    'calculate_cases_by_severity',
    'calculate_ai_review_distribution',
    'calculate_ai_agreement_rate',
    'calculate_corrected_diagnoses',
    'calculate_insufficient_evidence_cases',
    'calculate_osi_layer_distribution',
    'calculate_rule_checker_findings'
]