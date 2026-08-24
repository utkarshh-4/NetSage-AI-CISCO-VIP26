# NetSage AI — Architecture Documentation

## System Overview

NetSage AI is a Python-based network troubleshooting assistant that combines deterministic rule-based analysis with optional AI-powered diagnosis for Cisco/Packet Tracer network scenarios. The system prioritizes data integrity, human oversight, and responsible AI practices.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     NetSage AI System                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐  │
│  │   Streamlit  │      │   Batch      │      │   Unit       │  │
│  │   Dashboard  │      │ Validation   │      │   Tests      │  │
│  └──────┬───────┘      └──────┬───────┘      └──────┬───────┘  │
│         │                     │                     │          │
│         └─────────────────────┴─────────────────────┘          │
│                           │                                     │
│                    ┌──────▼──────┐                               │
│                    │   Main API   │                               │
│                    └──────┬──────┘                               │
│                           │                                     │
│         ┌─────────────────┼─────────────────┐                   │
│         │                 │                 │                   │
│  ┌──────▼──────┐   ┌──────▼──────┐   ┌──────▼──────┐           │
│  │   Data      │   │   Rules     │   │     AI      │           │
│  │   Loader    │   │   Checker   │   │   Diagnose  │           │
│  └──────┬──────┘   └──────┬──────┘   └──────┬──────┘           │
│         │                 │                 │                   │
│         └─────────────────┼─────────────────┘                   │
│                           │                                     │
│                    ┌──────▼──────┐                               │
│                    │   Review    │                               │
│                    │   Manager   │                               │
│                    └──────┬──────┘                               │
│                           │                                     │
│                    ┌──────▼──────┐                               │
│                    │  Analytics  │                               │
│                    │   Metrics   │                               │
│                    └─────────────┘                               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Component Architecture

### 1. Data Layer (`data/`)

**Purpose**: Load, validate, and provide access to network troubleshooting cases.

**Components**:
- `data_loader.py`: CSV loading with validation
- `cases.csv`: Evaluator-provided dataset (30 cases, read-only)

**Key Functions**:
- `load_cases()`: Load cases.csv with validation
- `get_case_by_id()`: Retrieve specific case
- `get_case_count()`: Get total case count

**Validation**:
- CSV file existence
- Required columns presence
- Duplicate case IDs
- Missing values
- Data integrity checks

**Data Model**:
```python
Case:
  - case_id: str (NET-001 to NET-030)
  - symptom: str (reported network issue)
  - topology_note: str (network topology description)
  - show_outputs: str (command outputs from devices)
  - expected_fault: str (expected fault for reference)
  - osi_layer: str (Layer 1-7)
  - concept_tag: str (network concept category)
  - severity: str (High/Medium/Low)
```

### 2. Rule Checker (`rules/`)

**Purpose**: Implement deterministic Python functions to identify common network issues.

**Components**:
- `checker.py`: Rule orchestrator
- `result_types.py`: Check result data structures
- `ip_checks.py`: IP address validation rules
- `interface_checks.py`: Interface state rules
- `vlan_checks.py`: VLAN configuration rules
- `routing_checks.py`: Routing protocol rules

**Implemented Rules**:
1. **Duplicate IP Detection** (`check_duplicate_ips`)
   - Identifies duplicate IP address conflicts
   - Parses show outputs for "duplicate" and "DUP_ADDR" keywords
   - Returns: DETECTED/NOT_DETECTED/INSUFFICIENT_EVIDENCE

2. **Subnet Mask Validation** (`check_subnet_mask`)
   - Validates subnet mask correctness
   - Identifies mismatched or invalid subnet masks
   - Returns: DETECTED/NOT_DETECTED/INSUFFICIENT_EVIDENCE

3. **Gateway Mismatch Detection** (`check_gateway_mismatch`)
   - Identifies gateway configuration issues
   - Compares configured gateway with topology
   - Returns: DETECTED/NOT_DETECTED/INSUFFICIENT_EVIDENCE

4. **Interface Down Detection** (`check_interface_down`)
   - Detects administratively down interfaces
   - Identifies shutdown interfaces
   - Returns: DETECTED/NOT_DETECTED/INSUFFICIENT_EVIDENCE

5. **Missing VLAN Detection** (`check_missing_vlan`)
   - Identifies missing or incorrect VLAN configurations
   - Checks access VLAN assignments
   - Returns: DETECTED/NOT_DETECTED/INSUFFICIENT_EVIDENCE

6. **Missing Route Detection** (`check_missing_routes`)
   - Identifies missing or unreachable static routes
   - Validates next-hop reachability
   - Returns: DETECTED/NOT_DETECTED/INSUFFICIENT_EVIDENCE

**Data Model**:
```python
CheckResult:
  - check_name: str (rule identifier)
  - status: str (DETECTED/NOT_DETECTED/INSUFFICIENT_EVIDENCE)
  - message: str (human-readable explanation)
  - evidence: List[str] (supporting evidence)
  - confidence: str (high/medium/low)
```

### 3. AI Diagnosis (`ai/`)

**Purpose**: Provide LLM-powered network diagnosis with structured responses.

**Components**:
- `diagnose.py`: OpenAI API integration
- `schemas.py`: Pydantic validation schemas
- `prompts.py`: Prompt management

**Process Flow**:
1. Evidence collection from case data
2. Rule checker results integration
3. Prompt construction with worked examples
4. OpenAI API call (gpt-3.5-turbo default)
5. Response validation against Pydantic schema
6. Error handling for API failures

**AI Response Schema**:
```python
DiagnosisResponse:
  - root_cause: str (primary diagnosis)
  - confidence: ConfidenceLevel (high/medium/low)
  - evidence: List[EvidenceItem] (supporting evidence)
  - next_command: Optional[str] (next diagnostic command)
  - fix_steps: List[FixStep] (sequential fix steps)
  - osi_layer: OSILayer (Layer 1-7)
  - issue_type: str (network issue category)
  - severity: SeverityLevel (high/medium/low)
  - alternative_causes: List[AlternativeCause] (alternative possibilities)
  - limitations: List[str] (known limitations)
  - notes: Optional[str] (additional context)
  - requires_human_review: bool (always true)

EvidenceItem:
  - source: str (evidence source)
  - content: str (actual evidence)
  - type: str (observed/inferred)

FixStep:
  - step_number: int (sequence number)
  - command: str (command to execute)
  - explanation: str (what this step does)
  - verification: Optional[str] (how to verify)
```

**Key Features**:
- Evidence grounding (uses only supplied evidence)
- Uncertainty handling (states "insufficient evidence" vs guessing)
- No auto-apply (fix steps require human execution)
- Human review required (always true)

### 4. Human Review (`review/`)

**Purpose**: Implement mandatory human oversight for AI diagnoses.

**Components**:
- `review_manager.py`: Review workflow management
- `schemas.py`: Review data models

**Review Process**:
1. AI diagnosis generated
2. Expert reviews in Streamlit interface
3. Expert selects decision: ACCEPT/EDIT/REJECT
4. Expert provides notes and reasoning
5. Review manager stores decision
6. Final diagnosis determined
7. Metrics updated

**Review Schema**:
```python
ReviewDecision: Enum
  - ACCEPTED: AI diagnosis correct as-is
  - EDITED: AI needs correction
  - REJECTED: AI incorrect

ReviewRecord:
  - case_id: str (case identifier)
  - timestamp: datetime (review timestamp)
  - ai_diagnosis: Dict[str, Any] (original AI response)
  - reviewer_decision: ReviewDecision (expert decision)
  - corrected_diagnosis: Optional[Dict[str, Any]] (modified diagnosis)
  - reviewer_notes: Optional[str] (expert feedback)
  - reason_for_correction: Optional[str] (correction reasoning)
  - final_diagnosis: Dict[str, Any] (final diagnosis)
  - ai_human_agreed: bool (agreement status)
```

**Agreement Calculation**:
```python
agreement_rate = accepted_count / total_reviews
```

### 5. Analytics (`analytics/`)

**Purpose**: Calculate metrics and provide dashboard insights.

**Components**:
- `metrics.py`: Metric calculation functions
- `__init__.py`: Package exports

**Calculated Metrics**:
- Total cases
- Cases by issue type (concept_tag)
- Cases by severity (High/Medium/Low)
- AI review distribution (Accepted/Edited/Rejected)
- AI-vs-human agreement rate
- Corrected diagnosis count
- Insufficient evidence count
- OSI layer distribution
- Rule checker findings by category

**Data Flow**:
```
Data Sources → Metric Functions → Dashboard Visualization
```

### 6. Streamlit Dashboard (`dashboard/`)

**Purpose**: Provide interactive web interface for case analysis.

**Components**:
- `app.py`: Streamlit application
- `__init__.py`: Package initialization

**Dashboard Pages**:
1. **Case Selection**: Select and view cases
2. **Rule Checks**: View deterministic rule results
3. **AI Diagnosis**: Run and view AI diagnoses
4. **Human Review**: Review and approve/edit/reject AI
5. **Verification**: Track fix verification
6. **Responsible AI**: View AI performance statistics
7. **Analytics Dashboard**: Comprehensive metrics and charts

**Session State Management**:
- Loaded cases
- Selected case
- Rule results
- AI diagnosis/error
- Review decision/notes
- Corrected diagnosis
- Verification state/notes
- Developer mode
- Review manager

### 7. Batch Validation (`batch_validation.py`)

**Purpose**: Process entire dataset without Streamlit UI for automated validation.

**Process**:
1. Load all cases from cases.csv
2. For each case:
   - Validate data
   - Run deterministic rules
   - Run AI diagnosis (if API available)
   - Validate AI schema
   - Compare with expected_fault
   - Record results
3. Generate summary statistics
4. Save results to JSON/CSV

**Output Files**:
- `validation_results/summary_<timestamp>.json`
- `validation_results/detailed_results_<timestamp>.json`
- `validation_results/results_<timestamp>.csv`

**Summary Metrics**:
- Total cases
- Successfully processed
- Rule-checker failures
- AI failures
- Schema failures
- Insufficient-evidence cases
- AI/expected agreement
- Human accepted/edited/rejected

### 8. Prompt Library (`prompts/`)

**Purpose**: Provide structured AI prompts with worked examples.

**Components**:
- `diagnose_prompt.md`: Comprehensive prompt template

**Prompt Structure**:
- Role definition
- Core principles (evidence grounding, no hallucination)
- Case data structure explanation
- Required JSON response structure
- 3 worked examples (interface down, duplicate IP, insufficient evidence)
- Uncertainty rules
- Final reminders

**Key Principles**:
- Use only supplied evidence
- Reference actual evidence explicitly
- Separate evidence from inference
- Never invent commands/outputs
- State insufficiency explicitly
- Set appropriate confidence levels
- Recommend next commands
- Fix steps without execution claims
- Never auto-apply changes
- Respect deterministic checker
- Always require human review

## Data Flow Diagrams

### Case Analysis Flow
```
User selects case
       ↓
Data loader loads case
       ↓
Rule checker runs deterministic checks
       ↓
AI diagnosis (if API available)
       ↓
Human review (ACCEPT/EDIT/REJECT)
       ↓
Verification in Packet Tracer
       ↓
Analytics updated
```

### Batch Validation Flow
```
Load all cases
       ↓
For each case:
  - Validate data
  - Run rules
  - Run AI (if available)
  - Validate schema
  - Compare with expected
  - Record results
       ↓
Generate summary
       ↓
Save to JSON/CSV
```

### Responsible AI Flow
```
AI diagnosis generated
       ↓
Expert reviews in Streamlit
       ↓
Decision: ACCEPT/EDIT/REJECT
       ↓
Original AI preserved
       ↓
Review metadata stored
       ↓
Agreement metrics calculated
       ↓
Responsible AI log updated
```

## Error Handling Strategy

### Data Layer
- CSV file not found: Raise FileNotFoundError
- Invalid data: Raise ValueError with specific error
- Duplicate IDs: Raise ValueError
- Missing values: Raise ValueError

### Rule Checker
- Invalid case data: Return INSUFFICIENT_EVIDENCE
- Missing evidence: Return INSUFFICIENT_EVIDENCE
- Internal errors: Log and return NOT_DETECTED

### AI Diagnosis
- API key missing: Raise ValueError
- API rate limit: Return error response, log, continue
- API timeout: Return error response, log, continue
- Malformed response: Raise ValidationError
- Invalid JSON: Raise JSONDecodeError

### Human Review
- Invalid decision: Raise ValueError
- Missing case: Return None
- Database errors: Log and raise

### Batch Validation
- Case processing error: Log, continue to next case
- API failure: Record as AI failure, continue
- Schema validation: Record as schema failure, continue
- Summary generation: Log and raise if critical

## Security Considerations

### API Key Management
- API keys stored in environment variables only
- Never committed to version control
- .env.example provided (no real keys)
- Streamlit UI never displays API keys

### Data Integrity
- cases.csv treated as read-only
- Original evidence always preserved
- AI responses preserved before review
- No automatic network configuration changes

### Human Oversight
- All AI diagnoses require human review
- Fix steps require manual execution
- Verification requires manual confirmation
- Original AI responses never modified

## Performance Considerations

### Caching
- Case data loaded once per session
- Rule results cached in session state
- AI diagnoses cached in session state

### API Usage
- Batch validation supports SKIP_AI flag
- Graceful degradation when API unavailable
- Rate limit handling with retries

### Data Processing
- Pandas for efficient data manipulation
- Batch processing for large datasets
- Error recovery for individual case failures

## Testing Strategy

### Unit Tests
- Data loader validation
- Rule checker logic
- AI schema validation
- Review manager operations
- Analytics calculations

### Integration Tests
- Data → Rule checker integration
- Data → AI diagnosis integration
- Review → Analytics integration
- Batch validation end-to-end

### Dashboard Tests
- Component structure validation
- Security checks (no API key exposure)
- Error handling verification
- User experience validation

### Test Coverage
- 170 tests total
- All core functionality covered
- Error cases covered
- Edge cases covered

## Deployment Considerations

### Environment Requirements
- Python 3.11+
- OpenAI API key (for AI features)
- Streamlit server for UI
- File system for data storage

### Configuration
- Environment variables for API keys
- .env file for local development
- Streamlit config for UI settings

### Scalability
- Batch processing for large datasets
- Graceful degradation without AI
- Stateless Streamlit sessions
- File-based persistence

## Future Architecture Enhancements

### Potential Improvements
1. Database backend for review storage
2. Caching layer for AI responses
3. Alternative AI provider support
4. Advanced analytics with ML
5. Packet Tracer API integration
6. Real-time collaboration features
7. Export capabilities for academic analysis
8. Multi-language support

### Extensibility Points
- Rule checker: Add new rules in separate modules
- AI diagnosis: Support different models/providers
- Analytics: Add custom metrics
- Dashboard: Add new pages/components

## Compliance and Accountability

### Responsible AI Principles
- No fabrication of AI outputs
- Transparent reporting of limitations
- Mandatory human review
- Comprehensive logging
- Data integrity preservation

### Academic Integrity
- Original evidence preserved
- No fake data generation
- Honest reporting of system capabilities
- Clear documentation of limitations
- Responsible handling of API limitations

### Verification and Reproducibility
- All results stored in JSON/CSV
- Original cases.csv preserved
- Review metadata maintained
- Test suite for validation
- Clear methodology documentation