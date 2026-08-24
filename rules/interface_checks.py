"""Interface state checks for network troubleshooting."""

import re
from typing import Dict, List
from rules.result_types import CheckResult


def check_interface_down(case: Dict[str, str]) -> CheckResult:
    """
    Check for interfaces that are administratively or operationally down.
    
    Required evidence:
    - Show interface command output
    - Interface state information (administratively down, line protocol down)
    - Interface configuration details
    
    Returns:
        CheckResult with status DETECTED, NOT_DETECTED, INSUFFICIENT_EVIDENCE, or ERROR
    """
    check_name = "interface_down"
    show_outputs = case.get("show_outputs", "")
    topology_note = case.get("topology_note", "")
    symptom = case.get("symptom", "")
    
    evidence = []
    
    # Look for interface down indicators
    down_patterns = [
        r"administratively down",
        r"line protocol is down",
        r"err-disabled"
    ]
    
    for pattern in down_patterns:
        if re.search(pattern, show_outputs, re.IGNORECASE):
            evidence.append(f"Found pattern in show_outputs: {pattern}")
        if re.search(pattern, topology_note, re.IGNORECASE):
            evidence.append(f"Found pattern in topology_note: {pattern}")
    
    # Check for shutdown (but not "no shutdown")
    shutdown_match = re.search(r"\bshutdown\b", show_outputs + " " + topology_note, re.IGNORECASE)
    if shutdown_match:
        # Check if "no shutdown" appears in the same context
        combined_text = show_outputs + " " + topology_note
        if not re.search(r"no\s+shutdown", combined_text, re.IGNORECASE):
            evidence.append("Found 'shutdown' without 'no shutdown'")
    
    # Extract interface names if available
    interface_pattern = r"(GigabitEthernet\d+/\d+\.?\d*|FastEthernet\d+/\d+|Vlan\d+|Serial\d+/\d+/\d+)"
    interfaces = re.findall(interface_pattern, show_outputs + " " + topology_note)
    
    if interfaces and evidence:
        evidence.append(f"Interfaces mentioned: {', '.join(set(interfaces))}")
    
    if evidence:
        return CheckResult(
            check_name=check_name,
            status="DETECTED",
            severity="high",
            message="Interface down state detected",
            evidence=evidence,
            confidence="high"
        )
    
    # Check if we have interface information
    has_interface_info = bool(
        re.search(r"interface\s+(GigabitEthernet|FastEthernet|Serial|Vlan)\d+", show_outputs + " " + topology_note, re.IGNORECASE) or
        re.search(r"GigabitEthernet\d+/\d+|FastEthernet\d+/\d+|Serial\d+/\d+/\d+|Vlan\d+", show_outputs + " " + topology_note, re.IGNORECASE)
    )
    
    if has_interface_info:
        return CheckResult(
            check_name=check_name,
            status="NOT_DETECTED",
            severity="low",
            message="No interface down states detected in available evidence",
            evidence=["Interface information present, all interfaces appear up"],
            confidence="medium"
        )
    
    return CheckResult(
        check_name=check_name,
        status="INSUFFICIENT_EVIDENCE",
        severity="low",
        message="Insufficient evidence to determine interface state",
        evidence=["No interface information found in case data"],
        confidence="low"
    )
