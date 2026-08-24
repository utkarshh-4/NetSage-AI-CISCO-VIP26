"""Rule checker orchestrator for deterministic network troubleshooting."""

from typing import Dict, List, Any
import logging

from rules.result_types import CheckResult
from rules.ip_checks import check_duplicate_ips, check_subnet_mask, check_gateway_mismatch
from rules.interface_checks import check_interface_down
from rules.vlan_checks import check_missing_vlan
from rules.routing_checks import check_missing_routes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_all_checks(case: Dict[str, str]) -> List[CheckResult]:
    """
    Run all deterministic rule checks on a case.
    
    Args:
        case: Dictionary containing case data with keys:
              - case_id
              - symptom
              - topology_note
              - show_outputs
              - expected_fault
              - osi_layer
              - concept_tag
              - severity
    
    Returns:
        List of CheckResult objects from all checks
    """
    results = []
    
    logger.info(f"Running all checks for case {case.get('case_id', 'UNKNOWN')}")
    
    # IP checks
    results.append(check_duplicate_ips(case))
    results.append(check_subnet_mask(case))
    results.append(check_gateway_mismatch(case))
    
    # Interface checks
    results.append(check_interface_down(case))
    
    # VLAN checks
    results.append(check_missing_vlan(case))
    
    # Routing checks
    results.append(check_missing_routes(case))
    
    logger.info(f"Completed {len(results)} checks for case {case.get('case_id', 'UNKNOWN')}")
    
    return results


def run_specific_check(case: Dict[str, str], check_name: str) -> CheckResult:
    """
    Run a specific check on a case.
    
    Args:
        case: Dictionary containing case data
        check_name: Name of the check to run
    
    Returns:
        CheckResult from the specified check
    """
    check_functions = {
        "duplicate_ips": check_duplicate_ips,
        "subnet_mask": check_subnet_mask,
        "gateway_mismatch": check_gateway_mismatch,
        "interface_down": check_interface_down,
        "missing_vlan": check_missing_vlan,
        "missing_routes": check_missing_routes
    }
    
    if check_name not in check_functions:
        return CheckResult(
            check_name=check_name,
            status="ERROR",
            message=f"Unknown check name: {check_name}",
            evidence=[],
            confidence="low"
        )
    
    return check_functions[check_name](case)


def summarize_results(results: List[CheckResult]) -> Dict[str, Any]:
    """
    Summarize check results.
    
    Args:
        results: List of CheckResult objects
    
    Returns:
        Dictionary with summary statistics
    """
    total = len(results)
    detected = sum(1 for r in results if r.status == "DETECTED")
    not_detected = sum(1 for r in results if r.status == "NOT_DETECTED")
    insufficient = sum(1 for r in results if r.status == "INSUFFICIENT_EVIDENCE")
    errors = sum(1 for r in results if r.status == "ERROR")
    
    return {
        "total_checks": total,
        "detected": detected,
        "not_detected": not_detected,
        "insufficient_evidence": insufficient,
        "errors": errors,
        "findings": [r.to_dict() for r in results if r.status == "DETECTED"]
    }
