# NetSage AI Demo Script

## Case Selection: NET-001

**Title**: Interface Down - Inter-VLAN Routing Failure

**Symptom**: PC1 cannot reach Server1 in VLAN 30

**Topology**: PC1 on Fa0/1 (VLAN 10); Gateway on Router Sub-interface Gi0/0.10

**Show Output**: GigabitEthernet0/0.10 is administratively down line protocol is down

**Expected Fault**: Sub-interface administratively down

---

## Demo Script (5-10 minutes)

### Introduction (1 minute)

"Hello, today I'd like to demonstrate NetSage AI, a network troubleshooting assistant I developed for Cisco/Packet Tracer scenarios. The system combines deterministic rule-based analysis with optional AI-powered diagnosis to help identify network issues.

NetSage AI is designed for educational environments, where students can learn systematic troubleshooting with evidence-based analysis and mandatory human oversight for responsible AI deployment."

### Show Broken Topology (30 seconds)

"Let me show you the broken Packet Tracer topology. Here we have a simple network with PC1 in VLAN 10 trying to reach Server1 in VLAN 30. The inter-VLAN routing should be handled by this router sub-interface."

### Explain Symptom (30 seconds)

"The reported symptom is: PC1 cannot reach Server1 in VLAN 30. This suggests an issue with inter-VLAN routing, which could be caused by problems at Layer 2, Layer 3, or configuration issues."

### Show Show-Command Evidence (30 seconds)

"Here's the relevant show-command evidence from the router:

'GigabitEthernet0/0.10 is administratively down line protocol is down'

This is a clear show output indicating the router sub-interface is shutdown. This is the evidence our system will analyze."

### Run Deterministic Rule Checker (1 minute)

"Now let me run the deterministic rule checker. These are Python functions that analyze network evidence for common issues."

[Click "Run Rule Checks"]

"The rule checker ran 6 different checks:
- Duplicate IP detection: Not detected
- Subnet mask validation: Not detected
- Gateway mismatch: Not detected
- **Interface down: DETECTED** - The checker found 'administratively down' in the show output
- Missing VLAN: Not detected
- Missing route: Not detected

The rule checker correctly identified that the interface is administratively down with high confidence. This gives us immediate baseline analysis without needing AI."

### Run AI Diagnosis (1 minute)

"Now, if we had OpenAI API access available, we would run the AI diagnosis. The system would send the case evidence and rule checker results to an LLM for structured analysis.

However, in the current academic environment, we're using rule-based analysis only due to API quota limitations. This is actually a responsible design choice - the system functions perfectly with deterministic rules and degrades gracefully when AI is unavailable.

If AI were available, it would provide a structured diagnosis including root cause, confidence level, evidence citations, recommended next commands, and fix steps - all requiring mandatory human review before any action."

### Explain Root Cause, Evidence, Confidence, OSI Layer, Next Command (1 minute)

"Based on the rule checker findings, let me explain the diagnosis:

**Root Cause**: The router sub-interface Gi0/0.10 is administratively shutdown, preventing inter-VLAN routing between VLAN 10 and VLAN 30.

**Evidence**: The show output explicitly states 'administratively down line protocol is down' - this is direct observed evidence from the device.

**Confidence**: High - the evidence is clear and unambiguous.

**OSI Layer**: Layer 3 - this is a routing interface issue affecting network layer connectivity.

**Next Command**: We would typically run 'show ip interface brief' to verify the interface state, but in this case the evidence is already clear."

### Perform Human Review (1 minute)

"NetSage AI requires mandatory human review before accepting any diagnosis. This is a core responsible AI principle - all automated recommendations must be reviewed by a human expert."

[Navigate to Human Review page]

"Here I review the diagnosis. The rule checker correctly identified the interface down issue. I agree with this analysis, so I'll select ACCEPT."

[Select ACCEPT, add notes: "Rule checker correctly identified interface shutdown"]

"I'll add reviewer notes: 'Rule checker correctly identified interface shutdown based on clear show-command evidence.'"

[Click "Save Review"]

"The system has now saved this review, preserving the original analysis and my expert decision. This creates an audit trail for accountability."

### Apply Fix Manually in Packet Tracer (1 minute)

"Now I'll apply the fix manually in Packet Tracer. The fix steps are straightforward:

1. Enter configuration mode: `configure terminal`
2. Select the interface: `interface GigabitEthernet0/0.10`
3. Enable the interface: `no shutdown`

These are the exact commands that would be recommended by the system. NetSage AI never automatically applies network changes - all fixes require manual execution and verification."

### Verify Connectivity (30 seconds)

"After applying the fix, I verify connectivity by having PC1 ping Server1."

[Show ping successful]

"The ping is successful, confirming the fix resolved the issue. The inter-VLAN routing is now working."

### Show Final Status (30 seconds)

"Let me record the verification status."

[Navigate to Verification page]

"I'll select VERIFIED and add notes: 'Ping test successful, inter-VLAN routing restored.'"

[Click "Save Verification"]

"The system now has a complete record: from case selection through rule analysis, human review, fix application, and verification."

### Briefly Show Dashboard (1 minute)

"Let me show you the analytics dashboard that tracks system performance."

[Navigate to Analytics Dashboard]

"The dashboard shows:
- Total cases in our dataset: 30
- Cases by issue type and severity
- OSI layer distribution
- Rule checker findings by category

All metrics are calculated from real stored data only - no fabricated metrics. The dashboard provides insights into the types of network issues in our dataset and how the rule checker performs."

### Briefly Show Responsible AI (1 minute)

"Finally, let me show the Responsible AI section."

[Navigate to Responsible AI page]

"This page tracks AI performance and human oversight. Currently, we have zero real AI corrections because AI diagnosis wasn't available during our validation run due to API quota limitations.

This is documented in our Responsible AI evidence report. We could have fabricated corrections to meet quotas, but that would violate responsible AI principles. Instead, we honestly report the limitation.

The infrastructure is fully ready for complete Responsible AI compliance when API access is restored - we have the human review workflow, audit trails, and agreement tracking all implemented."

### Conclusion (30 seconds)

"In summary, NetSage AI provides:
- Deterministic rule-based analysis that works reliably
- Optional AI diagnosis with mandatory human review
- Comprehensive audit trails for accountability
- Honest reporting of capabilities and limitations

The system demonstrates responsible AI development by prioritizing data integrity and academic honesty over meeting quotas. All 170 tests pass, the documentation is comprehensive, and the project is ready for full AI-powered analysis when API access becomes available.

Thank you for watching this demonstration of NetSage AI."

---

## Demo Notes for Presenter

### Timing Breakdown

- Introduction: 1 minute
- Topology & Symptom: 1 minute
- Rule Checker: 1 minute
- AI Diagnosis explanation: 1 minute
- Diagnosis details: 1 minute
- Human Review: 1 minute
- Fix & Verification: 1.5 minutes
- Dashboard & Responsible AI: 2 minutes
- Conclusion: 0.5 minutes

**Total**: ~10 minutes

### Key Points to Emphasize

1. **Rule-Based Analysis Works**: The system is fully functional without AI
2. **Honest AI Limitations**: Clear explanation of API quota limitation
3. **Mandatory Human Review**: All diagnoses require expert oversight
4. **No Automatic Changes**: All fixes require manual execution
5. **Academic Integrity**: Honest reporting, no fabrication
6. **Comprehensive Testing**: All 170 tests pass
7. **Documentation**: Complete documentation available

### What to Skip if Time is Short

- Detailed explanation of all 6 rule checks (focus on the detected one)
- Detailed dashboard tour (just show overview)
- Detailed Responsible AI explanation (just mention honest reporting)

### Technical Depth Adjustment

**For Technical Audience**:
- Explain the Python rule checker implementation
- Show the Pydantic schema validation
- Reference specific code modules

**For Non-Technical Audience**:
- Focus on workflow and benefits
- Simplify technical details
- Emphasize responsible AI principles

### Preparation Checklist

- [ ] Streamlit dashboard running
- [ ] NET-001 case selected
- [ ] Packet Tracer topology open (NET-001 scenario)
- [ ] Practice the demo timing
- [ ] Prepare answers for potential questions

### Potential Questions and Answers

**Q: Why isn't AI diagnosis working?**
A: Due to OpenAI API quota limitations in the academic environment. The system is designed to work with rule-based analysis only and degrades gracefully.

**Q: How many real AI corrections do you have?**
A: Zero, because we haven't generated AI diagnoses. We chose honest reporting over fabricating corrections to meet quotas.

**Q: Is the system actually useful without AI?**
A: Yes, the rule checker successfully processes all 30 cases with 100% success rate. AI would provide additional insights for complex cases.

**Q: How long did it take to develop?**
A: The project evolved through multiple phases including data loading, rule checker, AI integration, human review, analytics, and comprehensive documentation.

**Q: What's the future of this project?**
A: The infrastructure is ready for full AI-powered analysis when API access is restored. Potential enhancements include more rules, additional AI providers, and advanced analytics.