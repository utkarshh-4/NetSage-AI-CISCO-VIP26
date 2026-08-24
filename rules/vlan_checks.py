"""VLAN configuration checks for network troubleshooting."""

import re
from typing import Dict, List
from rules.result_types import CheckResult


def check_missing_vlan(case: Dict[str, str]) -> CheckResult:
    """
    Check for missing or misconfigured VLANs.
    
    Required evidence:
    - VLAN configuration information
    - Trunk port allowed VLAN lists
    - Access port VLAN assignments
    - Show vlan or show interface switchport output
    
    Returns:
        CheckResult with status DETECTED, NOT_DETECTED, INSUFFICIENT_EVIDENCE, or ERROR
    """
    check_name = "missing_vlan"
    show_outputs = case.get("show_outputs", "")
    topology_note = case.get("topology_note", "")
    symptom = case.get("symptom", "")
    
    evidence = []
    
    # Look for missing VLAN indicators in show_outputs only (not descriptions)
    vlan_patterns = [
        r"VLAN.*missing",
        r"VLAN.*pruned",
        r"VLAN.*not.*allowed",
        r"missing.*from.*allowed.*list",
        r"wrong.*access.*vlan",
        r"VLAN.*mismatch"
    ]
    
    for pattern in vlan_patterns:
        if re.search(pattern, show_outputs, re.IGNORECASE):
            evidence.append(f"Found pattern in show_outputs: {pattern}")
    
    # Check for trunk allowed VLAN issues (only if trunk is configured)
    trunk_pattern = r"switchport trunk allowed vlan\s+(\d+(?:\s+\d+)*)"
    trunk_matches = re.findall(trunk_pattern, show_outputs)  # Only check show_outputs
    
    # Only apply trunk VLAN heuristic if we have an actual trunk configuration
    has_trunk_config = bool(re.search(r"switchport mode trunk", show_outputs + " " + topology_note, re.IGNORECASE))
    
    if trunk_matches and has_trunk_config:
        for allowed_vlans in trunk_matches:
            vlan_list = [int(v) for v in allowed_vlans.split()]
            # Check if common VLANs are missing (this is a heuristic)
            if 1 not in vlan_list:  # VLAN 1 is default
                evidence.append(f"VLAN 1 missing from allowed list: {allowed_vlans}")
    
    # Check for access port VLAN assignments
    access_pattern = r"switchport access vlan\s+(\d+)"
    access_matches = re.findall(access_pattern, show_outputs + " " + topology_note)
    
    if access_matches:
        for vlan in access_matches:
            # Check if VLAN 0 is assigned (invalid)
            if vlan == "0":
                evidence.append(f"Invalid VLAN assignment: VLAN 0")
    
    if evidence:
        return CheckResult(
            check_name=check_name,
            status="DETECTED",
            severity="high",
            message="VLAN configuration issue detected",
            evidence=evidence,
            confidence="high"
        )
    
    # Check if we have VLAN information
    has_vlan_info = bool(
        re.search(r"switchport\s+\w+", show_outputs + " " + topology_note, re.IGNORECASE) or
        re.search(r"interface.*vlan", show_outputs + " " + topology_note, re.IGNORECASE)
    )
    
    if has_vlan_info:
        return CheckResult(
            check_name=check_name,
            status="NOT_DETECTED",
            severity="low",
            message="No VLAN configuration issues detected in available evidence",
            evidence=["VLAN information present, no issues found"],
            confidence="medium"
        )
    
    return CheckResult(
        check_name=check_name,
        status="INSUFFICIENT_EVIDENCE",
        severity="low",
        message="Insufficient evidence to determine VLAN configuration status",
        evidence=["No VLAN information found in case data"],
        confidence="low"
    )
