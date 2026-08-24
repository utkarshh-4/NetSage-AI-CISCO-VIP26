"""IP address validation checks for network troubleshooting."""

import re
from typing import Dict, List
from rules.result_types import CheckResult


def check_duplicate_ips(case: Dict[str, str]) -> CheckResult:
    """
    Check for duplicate IP addresses in the case evidence.
    
    Required evidence:
    - Log messages indicating duplicate IP conflicts
    - Show command output with IP address assignments
    
    Returns:
        CheckResult with status DETECTED, NOT_DETECTED, INSUFFICIENT_EVIDENCE, or ERROR
    """
    check_name = "duplicate_ips"
    show_outputs = case.get("show_outputs", "")
    symptom = case.get("symptom", "")
    topology_note = case.get("topology_note", "")
    
    evidence = []
    
    # Look for duplicate IP log messages
    dup_patterns = [
        r"Duplicate address",
        r"DUP_ADDR",
        r"IP address conflict",
        r"duplicate IP"
    ]
    
    for pattern in dup_patterns:
        if re.search(pattern, show_outputs, re.IGNORECASE):
            evidence.append(f"Found pattern in show_outputs: {pattern}")
    
    if re.search(pattern, symptom, re.IGNORECASE):
        evidence.append(f"Found pattern in symptom: {pattern}")
    
    if re.search(pattern, topology_note, re.IGNORECASE):
        evidence.append(f"Found pattern in topology_note: {pattern}")
    
    # If evidence found, return DETECTED
    if evidence:
        return CheckResult(
            check_name=check_name,
            status="DETECTED",
            severity="high",
            message="Duplicate IP address detected in network evidence",
            evidence=evidence,
            confidence="high"
        )
    
    # Check if we have enough evidence to make a determination
    has_ip_info = bool(
        re.search(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", show_outputs) or
        re.search(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", topology_note)
    )
    
    if has_ip_info:
        return CheckResult(
            check_name=check_name,
            status="NOT_DETECTED",
            severity="low",
            message="No duplicate IP addresses detected in available evidence",
            evidence=["IP address information present, no duplicates found"],
            confidence="medium"
        )
    
    return CheckResult(
        check_name=check_name,
        status="INSUFFICIENT_EVIDENCE",
        severity="low",
        message="Insufficient evidence to determine duplicate IP status",
        evidence=["No IP address information found in case data"],
        confidence="low"
    )


def check_subnet_mask(case: Dict[str, str]) -> CheckResult:
    """
    Check for incorrect subnet mask configurations.
    
    Required evidence:
    - IP address and subnet mask pairs
    - Subnet boundary information
    - Show command output with interface configurations
    
    Returns:
        CheckResult with status DETECTED, NOT_DETECTED, INSUFFICIENT_EVIDENCE, or ERROR
    """
    check_name = "subnet_mask"
    show_outputs = case.get("show_outputs", "")
    topology_note = case.get("topology_note", "")
    
    evidence = []
    
    # Look for subnet mask issues
    mask_patterns = [
        r"mask\s+\d+\.\d+\.\d+\.\d+.*outside.*subnet",
        r"subnet.*boundary",
        r"incorrect.*mask",
        r"wrong.*subnet"
    ]
    
    for pattern in mask_patterns:
        if re.search(pattern, show_outputs, re.IGNORECASE):
            evidence.append(f"Found pattern in show_outputs: {pattern}")
        if re.search(pattern, topology_note, re.IGNORECASE):
            evidence.append(f"Found pattern in topology_note: {pattern}")
    
    # Check for specific subnet mask format issues
    # Look for IP/mask notation and validate
    ip_mask_pattern = r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})/(\d+)"
    matches = re.findall(ip_mask_pattern, show_outputs + " " + topology_note)
    
    for ip, mask_len in matches:
        try:
            mask_int = int(mask_len)
            if mask_int < 0 or mask_int > 32:
                evidence.append(f"Invalid subnet mask length: /{mask_int} for IP {ip}")
        except ValueError:
            evidence.append(f"Invalid subnet mask format: {mask_len}")
    
    if evidence:
        return CheckResult(
            check_name=check_name,
            status="DETECTED",
            severity="high",
            message="Subnet mask configuration issue detected",
            evidence=evidence,
            confidence="high"
        )
    
    # Check if we have subnet information
    has_subnet_info = bool(
        re.search(r"/\d{1,2}", show_outputs + " " + topology_note) or
        re.search(r"255\.255", show_outputs + " " + topology_note)
    )
    
    if has_subnet_info:
        return CheckResult(
            check_name=check_name,
            status="NOT_DETECTED",
            severity="low",
            message="No subnet mask issues detected in available evidence",
            evidence=["Subnet mask information present, no issues found"],
            confidence="medium"
        )
    
    return CheckResult(
        check_name=check_name,
        status="INSUFFICIENT_EVIDENCE",
        severity="low",
        message="Insufficient evidence to determine subnet mask status",
        evidence=["No subnet mask information found in case data"],
        confidence="low"
    )


def check_gateway_mismatch(case: Dict[str, str]) -> CheckResult:
    """
    Check for default gateway misconfigurations.
    
    Required evidence:
    - Host IP configuration
    - Default gateway configuration
    - Subnet information to validate gateway is in correct subnet
    
    Returns:
        CheckResult with status DETECTED, NOT_DETECTED, INSUFFICIENT_EVIDENCE, or ERROR
    """
    check_name = "gateway_mismatch"
    show_outputs = case.get("show_outputs", "")
    topology_note = case.get("topology_note", "")
    symptom = case.get("symptom", "")
    
    evidence = []
    
    # Look for gateway mismatch indicators
    gateway_patterns = [
        r"gateway.*misconfig",
        r"default gateway.*wrong",
        r"gateway.*outside.*subnet",
        r"gateway.*mismatch"
    ]
    
    for pattern in gateway_patterns:
        if re.search(pattern, show_outputs, re.IGNORECASE):
            evidence.append(f"Found pattern in show_outputs: {pattern}")
        if re.search(pattern, topology_note, re.IGNORECASE):
            evidence.append(f"Found pattern in topology_note: {pattern}")
        if re.search(pattern, symptom, re.IGNORECASE):
            evidence.append(f"Found pattern in symptom: {pattern}")
    
    # Extract IP and gateway information for validation
    ip_pattern = r"IP\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
    gateway_pattern = r"Gateway\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
    
    ips = re.findall(ip_pattern, show_outputs + " " + topology_note)
    gateways = re.findall(gateway_pattern, show_outputs + " " + topology_note)
    
    if ips and gateways:
        # Basic validation: check if gateway is mentioned as outside subnet
        for gateway in gateways:
            if re.search(r"outside.*subnet", show_outputs + " " + topology_note, re.IGNORECASE):
                evidence.append(f"Gateway {gateway} is outside subnet boundary")
    
    if evidence:
        return CheckResult(
            check_name=check_name,
            status="DETECTED",
            severity="high",
            message="Default gateway misconfiguration detected",
            evidence=evidence,
            confidence="high"
        )
    
    # Check if we have gateway information
    has_gateway_info = bool(
        re.search(r"gateway", show_outputs + " " + topology_note, re.IGNORECASE) or
        re.search(r"default.*gateway", symptom, re.IGNORECASE)
    )
    
    if has_gateway_info:
        return CheckResult(
            check_name=check_name,
            status="NOT_DETECTED",
            severity="low",
            message="No gateway misconfiguration detected in available evidence",
            evidence=["Gateway information present, no mismatch found"],
            confidence="medium"
        )
    
    return CheckResult(
        check_name=check_name,
        status="INSUFFICIENT_EVIDENCE",
        severity="low",
        message="Insufficient evidence to determine gateway configuration status",
        evidence=["No gateway information found in case data"],
        confidence="low"
    )
