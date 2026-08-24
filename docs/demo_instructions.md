# Demo Instructions

## Overview

This document provides step-by-step instructions for demonstrating the NetSage AI system. The demo showcases the complete workflow from case selection through verification.

## Demo Preparation

### Prerequisites

- Python 3.11+ installed
- Virtual environment activated
- Dependencies installed
- Streamlit dashboard running
- Optional: OpenAI API key configured (for AI diagnosis)

### Start the Dashboard

```bash
streamlit run dashboard/app.py
```

Open the displayed URL (typically `http://localhost:8501`) in your browser.

## Demo Scenarios

### Demo 1: Interface Down Case (NET-001)

**Purpose**: Demonstrate rule checker detecting interface shutdown

**Steps**:

1. **Case Selection**
   - Navigate to "Case Selection"
   - Select "NET-001" from dropdown
   - Review case information:
     - Symptom: "PC1 cannot reach Server1 in VLAN 30"
     - Topology: "PC1 on Fa0/1 (VLAN 10); Gateway on Router Sub-interface Gi0/0.10"
     - Show Output: "GigabitEthernet0/0.10 is administratively down line protocol is down"

2. **Rule Checks**
   - Navigate to "Rule Checks"
   - Click "Run Rule Checks"
   - Review results:
     - **Interface Down**: DETECTED - "Interface is administratively down"
     - Evidence: ["administratively down", "line protocol is down"]
     - Confidence: high
   - Explain: The rule checker correctly identified the shutdown interface

3. **AI Diagnosis** (Optional - requires API key)
   - Navigate to "AI Diagnosis"
   - Click "Run AI Diagnosis"
   - Review AI diagnosis:
     - Root Cause: "Router sub-interface administratively shutdown"
     - Confidence: high
     - Evidence: Cites show output
     - Fix Steps: Enable interface with "no shutdown"
   - Explain: AI agrees with rule checker and provides fix steps

4. **Human Review**
   - Navigate to "Human Review"
   - Review AI diagnosis
   - Select: ACCEPT
   - Notes: "AI correctly identified interface down issue"
   - Click "Save Review"

5. **Verification**
   - Navigate to "Verification"
   - Apply fix in Packet Tracer (not part of demo)
   - Select: VERIFIED
   - Notes: "PC1 can now reach Server1"
   - Click "Save Verification"

**Key Points**:
- Rule checker provides immediate deterministic analysis
- AI diagnosis provides structured fix steps
- Human review ensures expert oversight
- Verification tracks actual fix in Packet Tracer

### Demo 2: Duplicate IP Case (NET-023)

**Purpose**: Demonstrate rule checker detecting IP conflicts

**Steps**:

1. **Case Selection**
   - Select "NET-023"
   - Review case:
     - Symptom: "Duplicate IP address conflict detected on LAN"
     - Show Output: "Log: %IP-4-DUP_ADDR: Duplicate address 192.168.1.100"

2. **Rule Checks**
   - Run rule checks
   - Review results:
     - **Duplicate IP**: DETECTED - "Duplicate IP address detected"
     - Evidence: ["DUP_ADDR", "Duplicate address"]
   - Explain: Rule checker found log evidence of duplicate IP

3. **AI Diagnosis** (Optional)
   - Run AI diagnosis
   - Review AI response:
     - Root Cause: "Two hosts configured with same IP"
     - Next Command: "show ip arp"
     - Fix Steps: Identify hosts, reconfigure one host
   - Explain: AI recommends ARP table analysis

**Key Points**:
- Rule checker identifies IP conflicts from log messages
- AI provides additional diagnostic commands
- Fix steps include verification methods

### Demo 3: Insufficient Evidence Case (NET-009)

**Purpose**: Demonstrate handling of insufficient evidence

**Steps**:

1. **Case Selection**
   - Select "NET-009"
   - Review case:
     - Symptom: "PC3 gets correct IP but cannot ping default gateway 192.168.1.1"
     - Topology: "PC3 IP 192.168.1.50/24; Gateway set to 192.168.1.254"

2. **Rule Checks**
   - Run rule checks
   - Review results:
     - **Gateway Mismatch**: INSUFFICIENT_EVIDENCE
     - Explain: Not enough information to determine mismatch

3. **AI Diagnosis** (Optional)
   - Run AI diagnosis
   - Review AI response:
     - Confidence: medium
     - Next Command: "ipconfig /all"
     - Limitations: Cannot verify actual gateway configuration
   - Explain: AI honestly states uncertainty

**Key Points**:
- System handles insufficient evidence gracefully
- AI sets appropriate confidence level
- AI recommends next diagnostic commands
- System does not fabricate diagnosis

### Demo 4: Batch Validation

**Purpose**: Demonstrate automated processing of entire dataset

**Steps**:

1. **Open Terminal**
   - Navigate to project directory
   - Run: `$env:SKIP_AI="true"; python batch_validation.py`

2. **Review Output**
   - Observe processing of 30 cases
   - Note 100% success rate
   - Review summary statistics

3. **Check Results**
   - Navigate to `validation_results/`
   - Open summary JSON file
   - Review detailed results

**Key Points**:
- Batch validation processes entire dataset
- Rule-based analysis works without AI
- Results saved in JSON/CSV formats
- System maintains data integrity

### Demo 5: Analytics Dashboard

**Purpose**: Demonstrate system performance metrics

**Steps**:

1. **Navigate to Analytics**
   - Click "Analytics Dashboard" in sidebar

2. **Review Metrics**
   - Total cases: 30
   - Cases by issue type
   - Cases by severity
   - OSI layer distribution
   - Rule checker findings

3. **Interact with Charts**
   - Hover over charts for details
   - Zoom in on specific data points
   - Filter by clicking legend items

**Key Points**:
- Dashboard provides comprehensive insights
- Interactive visualizations
- Real data only (no fabricated metrics)
- Clear methodology documentation

## Demo Script

### Opening Script

"Welcome to NetSage AI, an AI-assisted network troubleshooting application for Cisco/Packet Tracer scenarios. The system combines deterministic rule-based analysis with optional AI-powered diagnosis, all with mandatory human review for responsible AI deployment."

### Workflow Script

"I'll demonstrate the complete workflow:

1. First, we select a network troubleshooting case from our dataset of 30 cases
2. Then we run deterministic rule checks that immediately identify common issues
3. Next, we can optionally run AI diagnosis for complex analysis
4. Human review is mandatory - all AI diagnoses require expert approval
5. Finally, we track verification in Packet Tracer"

### Responsible AI Script

"NetSage AI demonstrates responsible AI practices:
- No fabrication of results when API unavailable
- Mandatory human review before any action
- Evidence-based analysis using only supplied data
- Comprehensive audit trail of all decisions
- Honest reporting of capabilities and limitations"

### Closing Script

"The system is fully functional for rule-based analysis and ready for complete AI-powered analysis when API access is restored. All documentation is comprehensive, all 170 tests pass, and the project demonstrates academic integrity with honest reporting of limitations."

## Troubleshooting Demo Issues

### Issue: Dashboard Won't Start

**Solution**:
- Ensure virtual environment activated
- Check Streamlit installed: `streamlit version`
- Reinstall if needed: `pip install streamlit>=1.28.0`

### Issue: AI Diagnosis Fails

**Solution**:
- This is expected if no API key configured
- Explain system works with rule-based analysis only
- Set SKIP_AI=true for demo without AI

### Issue: Cases Not Loading

**Solution**:
- Verify cases.csv exists in data/ directory
- Check file permissions
- Run data loader tests: `pytest tests/test_data.py`

### Issue: Rule Checks Not Running

**Solution**:
- Ensure case selected first
- Check rule checker module: `pytest tests/test_rules.py`
- Verify case data is valid

## Demo Tips

### For Academic Evaluation

1. **Emphasize Technical Quality**: Show all 170 tests passing
2. **Highlight Responsible AI**: Explain honest reporting of limitations
3. **Demonstrate Completeness**: Show all 7 dashboard pages
4. **Explain Architecture**: Reference architecture documentation
5. **Discuss Limitations**: Be transparent about API limitations

### For Technical Audience

1. **Show Code**: Reference specific modules and functions
2. **Explain Schemas**: Show Pydantic validation
3. **Demonstrate Testing**: Run test suite during demo
4. **Show Documentation**: Reference comprehensive docs
5. **Discuss Integration**: Explain component interaction

### For Non-Technical Audience

1. **Focus on Workflow**: Show step-by-step process
2. **Explain Benefits**: Highlight human oversight
3. **Simplify Technical**: Use analogies for complex concepts
4. **Emphasize Safety**: Show no automatic changes
5. **Show Usability**: Demonstrate intuitive interface

## Demo Preparation Checklist

- [ ] Python 3.11+ installed
- [ ] Virtual environment activated
- [ ] Dependencies installed
- [ ] Streamlit dashboard running
- [ ] cases.csv present in data/ directory
- [ ] Test suite passing (170/170)
- [ ] Documentation accessible
- [ ] Demo cases selected and rehearsed
- [ ] Troubleshooting steps prepared
- [ ] Opening/closing scripts prepared

## Demo Duration

- **Quick Demo**: 5-10 minutes (single case walkthrough)
- **Standard Demo**: 15-20 minutes (multiple cases + analytics)
- **Comprehensive Demo**: 30-45 minutes (all features + documentation)

## Summary

The NetSage AI demo showcases a complete, responsible AI-powered network troubleshooting system. The demo highlights technical quality, responsible AI practices, comprehensive documentation, and honest reporting of capabilities and limitations. The system is fully functional for rule-based analysis and ready for complete AI-powered analysis when API access is restored.