# Rule Checker Explanation

## Overview

The rule checker is a deterministic Python-based system that analyzes network troubleshooting cases to identify common network issues. It provides evidence-based findings without relying on AI or machine learning, ensuring consistent and reproducible results.

## Purpose

The rule checker serves three primary purposes:

1. **Baseline Analysis**: Provides immediate deterministic analysis for common network issues
2. **AI Support**: Supplies structured findings to the AI diagnosis system as supporting evidence
3. **Fallback**: Operates when AI services are unavailable (e.g., API quota limitations)

## Architecture

### Component Structure

```
rules/
├── checker.py           # Rule orchestrator
├── result_types.py      # Data structures
├── ip_checks.py         # IP address validation
├── interface_checks.py  # Interface state checks
├── vlan_checks.py       # VLAN configuration checks
└── routing_checks.py    # Routing protocol checks
```

### Orchestrator (`checker.py`)

The orchestrator coordinates all rule checks:

```python
def run_all_checks(case: Dict[str, str]) -> List[CheckResult]:
    """
    Run all deterministic rule checks on a case.
    
    Returns:
        List of CheckResult objects from all checks
    """
    results = []
    
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
    
    return results
```

## Implemented Rules

### 1. Duplicate IP Detection (`check_duplicate_ips`)

**Purpose**: Identify duplicate IP address conflicts on the network.

**Detection Logic**:
- Searches show outputs for keywords: "duplicate", "DUP_ADDR"
- Analyzes IP address configurations
- Compares host configurations

**Example Detection**:
```
Input: "Log: %IP-4-DUP_ADDR: Duplicate address 192.168.1.100 on FastEthernet0/1"
Output: DETECTED - "Duplicate IP address 192.168.1.100 detected"
Evidence: ["DUP_ADDR", "Duplicate address"]
```

**Sample Case**: NET-023 (Duplicate IP address conflict detected on LAN)

### 2. Subnet Mask Validation (`check_subnet_mask`)

**Purpose**: Validate subnet mask correctness and identify mismatched masks.

**Detection Logic**:
- Parses subnet mask configurations
- Validates mask format (CIDR notation)
- Checks for mismatched masks in same subnet
- Identifies invalid mask lengths

**Example Detection**:
```
Input: "IP 10.1.1.50 mask 255.255.255.240; Gateway 10.1.1.30"
Output: DETECTED - "Gateway outside subnet range based on mask"
Evidence: ["mask 255.255.255.240", "Gateway 10.1.1.30"]
```

**Sample Case**: NET-020 (Default Gateway outside client subnet range)

### 3. Gateway Mismatch Detection (`check_gateway_mismatch`)

**Purpose**: Identify gateway configuration issues.

**Detection Logic**:
- Compares configured gateway with topology
- Checks for default gateway misconfiguration
- Validates gateway reachability

**Example Detection**:
```
Input: "PC3 IP 192.168.1.50/24; Gateway set to 192.168.1.254"
Output: DETECTED - "Gateway mismatch detected"
Evidence: ["Gateway 192.168.1.254", "subnet /24"]
```

**Sample Case**: NET-009 (Host Default Gateway IP Misconfiguration)

### 4. Interface Down Detection (`check_interface_down`)

**Purpose**: Detect administratively down or shutdown interfaces.

**Detection Logic**:
- Searches for "administratively down"
- Searches for "shutdown" in configuration
- Analyzes interface state from show commands

**Example Detection**:
```
Input: "GigabitEthernet0/0.10 is administratively down line protocol is down"
Output: DETECTED - "Interface is administratively down"
Evidence: ["administratively down", "line protocol is down"]
```

**Sample Case**: NET-001 (Sub-interface administratively down)

### 5. Missing VLAN Detection (`check_missing_vlan`)

**Purpose**: Identify missing or incorrect VLAN configurations.

**Detection Logic**:
- Analyzes switch port configurations
- Checks for missing access VLAN assignments
- Identifies incorrect VLAN tags
- Validates trunk allowed VLAN lists

**Example Detection**:
```
Input: "interface FastEthernet0/10; switchport access vlan 14"
Output: DETECTED - "Port assigned to wrong access VLAN"
Evidence: ["switchport access vlan 14"]
```

**Sample Case**: NET-013 (Switch port assigned to wrong access VLAN)

### 6. Missing Route Detection (`check_missing_routes`)

**Purpose**: Identify missing or unreachable static routes.

**Detection Logic**:
- Analyzes routing table configurations
- Validates next-hop IP addresses
- Checks for unreachable next-hops
- Identifies missing route entries

**Example Detection**:
```
Input: "ip route 172.16.0.0 255.255.0.0 10.0.0.5 (Next-hop IP 10.0.0.5 unreachable)"
Output: DETECTED - "Invalid static route next-hop IP address"
Evidence: ["Next-hop IP 10.0.0.5 unreachable"]
```

**Sample Case**: NET-015 (Invalid static route next-hop IP address)

## Data Structures

### CheckResult

```python
class CheckResult:
    """Result of a single rule check."""
    
    check_name: str          # Rule identifier (e.g., "duplicate_ips")
    status: str              # DETECTED, NOT_DETECTED, or INSUFFICIENT_EVIDENCE
    message: str             # Human-readable explanation
    evidence: List[str]      # Supporting evidence from case data
    confidence: str          # high, medium, or low
```

### Status Values

- **DETECTED**: Rule found evidence of the issue
- **NOT_DETECTED**: Rule found no evidence of the issue
- **INSUFFICIENT_EVIDENCE**: Not enough information to determine

## Rule Checker Process

### Input

Each rule receives a case dictionary:
```python
case = {
    "case_id": "NET-001",
    "symptom": "PC1 cannot reach Server1 in VLAN 30",
    "topology_note": "PC1 on Fa0/1 (VLAN 10); Gateway on Router Sub-interface Gi0/0.10",
    "show_outputs": "GigabitEthernet0/0.10 is administratively down line protocol is down",
    "expected_fault": "Sub-interface administratively down",
    "osi_layer": "Layer 3",
    "concept_tag": "Inter-VLAN Routing",
    "severity": "High"
}
```

### Processing

1. **Rule Selection**: Each rule analyzes the case data
2. **Evidence Extraction**: Rule searches relevant fields for keywords
3. **Logic Application**: Rule applies deterministic logic
4. **Result Generation**: Rule produces CheckResult with status

### Output

List of CheckResult objects:
```python
[
    CheckResult(
        check_name="interface_down",
        status="DETECTED",
        message="Interface is administratively down",
        evidence=["administratively down", "line protocol is down"],
        confidence="high"
    ),
    CheckResult(
        check_name="duplicate_ips",
        status="NOT_DETECTED",
        message="No duplicate IP addresses detected",
        evidence=[],
        confidence="high"
    ),
    ...
]
```

## Integration with AI Diagnosis

The rule checker results are provided to the AI diagnosis system as supporting evidence:

```python
# In AI diagnosis
rule_results = run_all_checks(case)
ai_diagnosis = diagnose_case(case, rule_results)
```

The AI prompt instructs the LLM to:
- Treat deterministic rule-checker findings as supporting evidence
- Not treat them as unquestionable truth
- Explain if it disagrees with checker findings

## Performance Characteristics

### Advantages

1. **Deterministic**: Same input always produces same output
2. **Fast**: No API calls, instant results
3. **Reliable**: No dependency on external services
4. **Transparent**: Clear logic and evidence
5. **Reproducible**: Results can be reproduced exactly

### Limitations

1. **Limited Scope**: Only covers 6 specific rule types
2. **No Generalization**: Cannot handle novel scenarios
3. **No Context**: Doesn't understand complex network interactions
4. **False Negatives**: May miss issues not covered by rules
5. **False Positives**: May flag issues in edge cases

## Usage Examples

### Basic Usage

```python
from rules.checker import run_all_checks
from data.data_loader import load_cases

# Load cases
df = load_cases()

# Get a specific case
case = df[df['case_id'] == 'NET-001'].iloc[0].to_dict()

# Run all checks
results = run_all_checks(case)

# Display results
for result in results:
    print(f"{result.check_name}: {result.status}")
    print(f"  Message: {result.message}")
    print(f"  Evidence: {result.evidence}")
    print()
```

### Running Specific Check

```python
from rules.interface_checks import check_interface_down

result = check_interface_down(case)
print(f"Status: {result.status}")
print(f"Message: {result.message}")
```

### Batch Processing

```python
from rules.checker import run_all_checks
from data.data_loader import load_cases

df = load_cases()
all_results = {}

for _, case in df.iterrows():
    case_dict = case.to_dict()
    results = run_all_checks(case_dict)
    all_results[case_dict['case_id']] = results
```

## Testing

The rule checker has comprehensive test coverage:

- **Unit Tests**: Each rule function tested individually
- **Integration Tests**: Full checker orchestration tested
- **Edge Cases**: Insufficient evidence scenarios tested
- **Sample Cases**: Real cases from dataset tested

### Running Rule Checker Tests

```bash
pytest tests/test_rules.py
```

## Current Performance

### Batch Validation Results

In the latest batch validation (30 cases):
- **Total Cases**: 30
- **Rule Checker Success Rate**: 100% (30/30)
- **Rule Checker Failures**: 0
- **Average Processing Time**: < 1 second per case

### Detection Statistics

Based on 30-case dataset:
- **DETECTED**: ~40% of checks find issues
- **NOT_DETECTED**: ~50% of checks find no issues
- **INSUFFICIENT_EVIDENCE**: ~10% of checks need more data

## Future Enhancements

### Potential Rule Additions

1. **ACL Rule Detection**: Identify ACL configuration issues
2. **NAT Rule Detection**: Identify NAT configuration problems
3. **OSPF Rule Detection**: Identify OSPF misconfigurations
4. **HSRP Rule Detection**: Identify HSRP timer mismatches
5. **VTP Rule Detection**: Identify VTP domain issues

### Enhancement Strategy

Rules should be added following these principles:
- High-frequency issues in real networks
- Clear detection criteria
- Deterministic logic (no ambiguity)
- Supporting evidence available in show outputs
- Testable with sample cases

## Conclusion

The rule checker provides a solid foundation for deterministic network troubleshooting analysis. While limited in scope compared to AI-powered diagnosis, it offers reliable, fast, and transparent analysis for common network issues. Its integration with the AI diagnosis system provides the best of both worlds: deterministic baseline analysis with AI-powered reasoning for complex scenarios.