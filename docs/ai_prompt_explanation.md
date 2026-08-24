# AI Prompt Explanation

## Overview

The AI prompt is a structured system prompt designed to guide the OpenAI LLM (GPT-3.5-turbo) in analyzing network troubleshooting cases. The prompt emphasizes evidence-based analysis, uncertainty handling, and responsible AI practices.

## Purpose

The AI prompt serves to:

1. **Define Role**: Establish the AI as an expert network troubleshooting assistant
2. **Enforce Principles**: Ensure evidence-based, responsible analysis
3. **Specify Structure**: Require structured JSON output
4. **Provide Examples**: Demonstrate expected behavior with worked examples
5. **Handle Uncertainty**: Guide behavior when evidence is insufficient

## Prompt Structure

The prompt (`prompts/diagnose_prompt.md`) consists of 8 main sections:

### 1. Role Definition

```
You are an expert network troubleshooting assistant specializing in 
Cisco/Packet Tracer network diagnosis. Your role is to analyze network 
troubleshooting cases and provide evidence-based diagnoses.
```

**Purpose**: Establish the AI's expertise and domain focus.

### 2. Core Principles

The prompt defines 12 core principles that govern AI behavior:

#### Principle 1: Use Only Supplied Evidence
- Base analysis ONLY on case evidence provided
- Do not invent, assume, or hallucinate network configurations
- Do not fabricate command outputs or device states

#### Principle 2: Reference Actual Evidence
- Explicitly reference actual show-command evidence
- Cite specific evidence sources in analysis

#### Principle 3: Separate Evidence from Inference
- Clearly distinguish between observed evidence and logical deductions
- Label evidence as "observed" or "inferred"

#### Principle 4: Never Invent Commands/Output
- Do not fabricate command outputs
- Do not fabricate configuration snippets
- Do not fabricate device states

#### Principle 5: State Insufficiency
- If evidence is insufficient, explicitly state this
- Do not guess when information is missing

#### Principle 6: Confidence Levels
- **high**: Strong, direct evidence supporting diagnosis
- **medium**: Some evidence but with gaps or ambiguity
- **low**: Limited or circumstantial evidence

#### Principle 7: Recommend Next Commands
- When evidence is insufficient, recommend next diagnostic commands
- Focus on commands that would provide missing information

#### Principle 8: Fix Steps Without Execution
- Provide fix steps but NEVER claim execution
- Always state fixes require human execution and verification

#### Principle 9: Never Auto-Apply Changes
- Never suggest automatic application of network changes
- All changes require human intervention

#### Principle 10: Respect Deterministic Checker
- Treat deterministic rule-checker findings as supporting evidence
- Not unquestionable truth
- Explain disagreements if they occur

#### Principle 11: Machine-Readable Output
- Return responses in specified JSON structure only
- No conversational text outside JSON

#### Principle 12: Human Review Required
- Always set requires_human_review to true
- AI diagnosis must be reviewed before action

### 3. Case Data Structure

The prompt explains the data the AI will receive:

```json
{
  "case_id": "Unique identifier",
  "symptom": "Reported network issue",
  "topology_note": "Network topology description",
  "show_outputs": "Actual command outputs from devices",
  "expected_fault": "Expected fault (for reference only)",
  "osi_layer": "OSI layer where issue is suspected",
  "concept_tag": "Network concept involved",
  "severity": "Issue severity"
}
```

Plus rule checker results:
```json
{
  "rule_results": {
    "duplicate_ips": {"status": "DETECTED", "evidence": [...]},
    "subnet_mask": {"status": "NOT_DETECTED", "evidence": [...]},
    ...
  }
}
```

### 4. Required JSON Response Structure

The prompt specifies the exact JSON structure required:

```json
{
  "root_cause": "Primary root cause of the issue",
  "confidence": "high|medium|low",
  "evidence": [
    {
      "source": "e.g., 'show ip interface', 'log message'",
      "content": "Actual evidence text",
      "type": "observed|inferred"
    }
  ],
  "next_command": "Next diagnostic command (or null)",
  "fix_steps": [
    {
      "step_number": 1,
      "command": "Command to execute",
      "explanation": "What this step does",
      "verification": "How to verify success (optional)"
    }
  ],
  "osi_layer": "Layer 1|Layer 2|Layer 3|Layer 4|Layer 5|Layer 6|Layer 7",
  "issue_type": "e.g., 'routing', 'switching', 'addressing'",
  "severity": "high|medium|low",
  "alternative_causes": [
    {
      "description": "Alternative cause description",
      "likelihood": "high|medium|low",
      "evidence": ["Evidence supporting this alternative"]
    }
  ],
  "limitations": ["Limitation 1", "Limitation 2"],
  "notes": "Additional context (optional)",
  "requires_human_review": true
}
```

### 5. Worked Examples

The prompt includes 3 detailed worked examples to demonstrate expected behavior:

#### Example 1: Interface Down

**Input**: Router sub-interface administratively down

**Key Elements**:
- Uses evidence from show_outputs: "administratively down"
- References rule checker detection
- Provides sequential fix steps
- Sets confidence to "high" (strong evidence)
- Includes verification steps

**Output**: Structured JSON with root cause, evidence, fix steps

#### Example 2: Duplicate IP Address

**Input**: Duplicate IP address conflict from log message

**Key Elements**:
- Uses evidence from log: "DUP_ADDR"
- Recommends next command: "show ip arp"
- Provides alternative cause analysis
- States limitations: cannot identify specific hosts
- Sets confidence to "high" (clear log evidence)

**Output**: Structured JSON with alternative causes and limitations

#### Example 3: Insufficient Evidence

**Input**: Gateway mismatch but unclear configuration

**Key Elements**:
- Uses evidence from topology and symptom
- Sets confidence to "medium" (some ambiguity)
- Recommends next command: "ipconfig /all"
- Provides alternative cause analysis
- States limitations: cannot verify actual gateway
- Sets requires_human_review to true

**Output**: Structured JSON with recommended next command and clear limitations

### 6. Uncertainty Rules

The prompt provides specific guidance for uncertain situations:

**When evidence is insufficient or ambiguous:**
1. Set confidence to "low" or "medium"
2. Clearly state what information is missing
3. Recommend next diagnostic commands
4. List alternative possible causes
5. Include limitations section
6. Do not make definitive claims without supporting evidence

### 7. Final Reminders

The prompt concludes with key reminders:
- Always return valid JSON
- Never claim a fix has been executed
- Always require human review
- Reference actual evidence from the case
- Distinguish observed from inferred evidence
- State limitations explicitly
- When in doubt, recommend more diagnostic commands rather than guessing

## Prompt Engineering Principles

### Evidence Grounding

The prompt uses several techniques to ensure evidence grounding:

1. **Explicit References**: Requires explicit citation of evidence sources
2. **Type Labels**: Distinguishes "observed" vs "inferred" evidence
3. **Insufficiency Declaration**: Requires stating when evidence is insufficient
4. **No Hallucination**: Explicitly prohibits inventing commands/outputs

### Uncertainty Handling

The prompt handles uncertainty through:

1. **Confidence Levels**: Three-tier confidence system
2. **Alternative Causes**: Requires listing alternative possibilities
3. **Limitations Section**: Mandatory documentation of limitations
4. **Next Commands**: Recommends diagnostic commands to reduce uncertainty

### Responsible AI

The prompt enforces responsible AI through:

1. **Human Review**: Always requires human review
2. **No Auto-Apply**: Prohibits automatic network changes
3. **Fix Without Execution**: Provides fix steps without claiming execution
4. **Evidence References**: Requires explicit evidence citations
5. **Limitations Documentation**: Requires transparency about limitations

## Integration with System

### Prompt Loading

```python
from ai.prompts import load_diagnose_prompt

prompt = load_diagnose_prompt()
```

### Prompt Application

```python
def diagnose_case(case, rule_results):
    prompt = load_diagnose_prompt()
    
    # Construct input with case data and rule results
    input_data = {
        "case_id": case["case_id"],
        "symptom": case["symptom"],
        ...
        "rule_results": rule_results
    }
    
    # Send to OpenAI API
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": json.dumps(input_data)}
        ]
    )
    
    return parse_response(response)
```

## Validation

### Schema Validation

The AI response is validated against Pydantic schema:

```python
from ai.schemas import DiagnosisResponse

try:
    diagnosis = DiagnosisResponse.model_validate_json(ai_response)
except ValidationError as e:
    # Handle validation error
    raise SchemaValidationError(str(e))
```

### Validation Checks

- Required fields present
- Confidence levels valid (high/medium/low)
- OSI layers valid (Layer 1-7)
- Severity levels valid (high/medium/low)
- Fix steps sequential (1, 2, 3...)
- Evidence array not empty
- requires_human_review is true

## Performance Characteristics

### Advantages

1. **Evidence-Based**: Forces AI to use only supplied evidence
2. **Structured Output**: Ensures consistent, parseable responses
3. **Uncertainty Handling**: Provides guidance for ambiguous cases
4. **Responsible AI**: Enforces human review and no auto-apply
5. **Explainable**: Clear trace from evidence to diagnosis

### Limitations

1. **Context Window**: Prompt length limits complexity
2. **Model Capability**: Depends on underlying LLM capabilities
3. **No Real-Time**: Cannot run actual commands
4. **Static Examples**: Worked examples may not cover all scenarios
5. **API Dependency**: Requires OpenAI API access

## Current Implementation

### Model Configuration

- **Default Model**: gpt-3.5-turbo
- **Temperature**: 0.7 (balanced creativity and consistency)
- **Max Tokens**: 2000 (sufficient for structured responses)

### Prompt Statistics

- **Total Length**: ~12,000 characters
- **Worked Examples**: 3 examples
- **Core Principles**: 12 principles
- **Expected Response Length**: ~500-1500 characters

## Testing

The prompt is tested through:

1. **Schema Validation**: All responses must pass Pydantic validation
2. **Evidence Check**: Responses must reference actual evidence
3. **Confidence Check**: Confidence levels must be appropriate
4. **Human Review Check**: requires_human_review must be true
5. **No Hallucination Check**: Responses must not invent evidence

### Running AI Tests

```bash
pytest tests/test_ai_diagnose.py
pytest tests/test_ai_schema.py
```

## Future Enhancements

### Potential Improvements

1. **More Worked Examples**: Add examples for additional scenarios
2. **Dynamic Prompt**: Customize prompt based on case type
3. **Few-Shot Learning**: Include relevant past cases as examples
4. **Chain-of-Thought**: Add explicit reasoning steps
5. **Confidence Calibration**: Improve confidence level assignment

### Enhancement Strategy

Prompt improvements should:
- Maintain evidence grounding principles
- Preserve uncertainty handling
- Keep human review requirement
- Test extensively with real cases
- Monitor for prompt injection vulnerabilities

## Conclusion

The AI prompt is a carefully engineered system prompt that enforces evidence-based, responsible AI analysis. Through explicit principles, worked examples, and structured output requirements, it ensures the AI provides useful, transparent, and accountable network troubleshooting assistance while requiring mandatory human oversight.