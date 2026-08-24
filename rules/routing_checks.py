"""Routing protocol checks for network troubleshooting."""

import re
from typing import Dict, List
from rules.result_types import CheckResult


def check_missing_routes(case: Dict[str, str]) -> CheckResult:
    """
    Check for missing or misconfigured routes.
    
    Required evidence:
    - Routing table information
    - Static route configurations
    - Dynamic routing protocol configuration (OSPF, EIGRP, etc.)
    - Show ip route command output
    
    Returns:
        CheckResult with status DETECTED, NOT_DETECTED, INSUFFICIENT_EVIDENCE, or ERROR
    """
    check_name = "missing_routes"
    show_outputs = case.get("show_outputs", "")
    topology_note = case.get("topology_note", "")
    symptom = case.get("symptom", "")
    
    evidence = []
    
    # Look for missing route indicators
    route_patterns = [
        r"missing.*route",
        r"route.*missing",
        r"no route",
        r"unreachable",
        r"next-hop.*unreachable",
        r"passive-interface",
        r"missing.*subnets"
    ]
    
    for pattern in route_patterns:
        if re.search(pattern, show_outputs, re.IGNORECASE):
            evidence.append(f"Found pattern in show_outputs: {pattern}")
        if re.search(pattern, topology_note, re.IGNORECASE):
            evidence.append(f"Found pattern in topology_note: {pattern}")
        if re.search(pattern, symptom, re.IGNORECASE):
            evidence.append(f"Found pattern in symptom: {pattern}")
    
    # Check for static route issues
    static_route_pattern = r"ip route\s+(\d+\.\d+\.\d+\.\d+)\s+(\d+\.\d+\.\d+\.\d+)\s+(\d+\.\d+\.\d+\.\d+)"
    static_routes = re.findall(static_route_pattern, show_outputs + " " + topology_note)
    
    for network, mask, next_hop in static_routes:
        # Check if next-hop is mentioned as unreachable
        if re.search(rf"{next_hop}.*unreachable", show_outputs + " " + topology_note, re.IGNORECASE):
            evidence.append(f"Static route next-hop {next_hop} unreachable for network {network}/{mask}")
    
    # Check for OSPF configuration issues
    ospf_patterns = [
        r"router ospf",
        r"network.*area",
        r"passive-interface"
    ]
    
    has_ospf = any(re.search(p, show_outputs + " " + topology_note, re.IGNORECASE) for p in ospf_patterns)
    
    if has_ospf:
        # Check for passive interface on active link
        passive_pattern = r"passive-interface\s+(\S+)"
        passive_matches = re.findall(passive_pattern, show_outputs + " " + topology_note)
        
        if passive_matches:
            for interface in passive_matches:
                evidence.append(f"Passive interface configured: {interface}")
    
    # Check for redistribution issues
    redistribution_pattern = r"redistribute\s+(\w+)"
    redistribution = re.findall(redistribution_pattern, show_outputs + " " + topology_note)
    
    if redistribution:
        for protocol in redistribution:
            # Check if subnets keyword is missing
            if re.search(rf"redistribute {protocol}", show_outputs + " " + topology_note, re.IGNORECASE):
                if not re.search(rf"redistribute {protocol}.*subnets", show_outputs + " " + topology_note, re.IGNORECASE):
                    evidence.append(f"Redistribution of {protocol} may be missing 'subnets' keyword")
    
    if evidence:
        return CheckResult(
            check_name=check_name,
            status="DETECTED",
            severity="high",
            message="Routing configuration issue detected",
            evidence=evidence,
            confidence="high"
        )
    
    # Check if we have routing information
    has_routing_info = bool(
        re.search(r"route|ospf|eigrp|rip|bgp", show_outputs + " " + topology_note, re.IGNORECASE) or
        re.search(r"routing", symptom, re.IGNORECASE)
    )
    
    if has_routing_info:
        return CheckResult(
            check_name=check_name,
            status="NOT_DETECTED",
            severity="low",
            message="No routing issues detected in available evidence",
            evidence=["Routing information present, no issues found"],
            confidence="medium"
        )
    
    return CheckResult(
        check_name=check_name,
        status="INSUFFICIENT_EVIDENCE",
        severity="low",
        message="Insufficient evidence to determine routing configuration status",
        evidence=["No routing information found in case data"],
        confidence="low"
    )
