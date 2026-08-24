# Dashboard Explanation

## Overview

The NetSage AI dashboard is a Streamlit-based web application that provides an interactive interface for network troubleshooting case analysis. It integrates rule-based checking, AI diagnosis, human review, and analytics into a unified user experience.

## Purpose

The dashboard serves to:

1. **Case Analysis**: Provide interactive case selection and viewing
2. **Rule Checking**: Display deterministic rule checker results
3. **AI Diagnosis**: Enable AI-powered diagnosis with expert review
4. **Human Review**: Facilitate expert review and approval workflow
5. **Verification**: Track fix verification in Packet Tracer
6. **Responsible AI**: Display AI performance and accountability metrics
7. **Analytics**: Provide comprehensive system performance insights

## Architecture

### Component Structure

```
dashboard/
├── app.py              # Streamlit application
└── __init__.py         # Package initialization
```

### Technology Stack

- **Streamlit 1.28+**: Web UI framework
- **Plotly 5.17+**: Interactive charts
- **Pandas 2.0+**: Data manipulation
- **Python 3.11+**: Core language

## Dashboard Pages

### Page 1: Case Selection

**Purpose**: Select and view network troubleshooting cases.

**Features**:
- Dropdown to select case from dataset
- Display case information:
  - Case ID
  - Symptom
  - Topology note
  - Show command outputs
  - Expected fault (developer mode only)
  - OSI layer
  - Concept tag
  - Severity

**Developer Mode**:
- Toggle to show expected fault for evaluator testing
- Hidden in normal diagnosis view to avoid bias

**Session State**:
- `selected_case`: Currently selected case
- `developer_mode`: Developer mode toggle

### Page 2: Rule Checks

**Purpose**: Display deterministic rule checker results.

**Features**:
- Button to run rule checks
- Display results for all 6 rules:
  - Duplicate IP detection
  - Subnet mask validation
  - Gateway mismatch detection
  - Interface down detection
  - Missing VLAN detection
  - Missing route detection

**Result Display**:
- Status (DETECTED/NOT_DETECTED/INSUFFICIENT_EVIDENCE)
- Message explaining the finding
- Supporting evidence
- Confidence level

**Session State**:
- `rule_results`: Rule checker results
- `rule_checks_run`: Whether checks have been executed

### Page 3: AI Diagnosis

**Purpose**: Run and view AI-powered diagnoses.

**Features**:
- Button to run AI diagnosis
- Display AI diagnosis:
  - Root cause
  - Confidence level
  - Evidence items (source, content, type)
  - Next recommended command
  - Fix steps (sequential with verification)
  - OSI layer
  - Issue type
  - Severity
  - Alternative causes
  - Limitations
  - Notes

**Error Handling**:
- Graceful error display if API unavailable
- Error message explaining limitation
- No fake diagnoses when API fails

**Session State**:
- `ai_diagnosis`: AI diagnosis response
- `ai_error`: Error message if AI fails
- `ai_diagnosis_run`: Whether AI has been executed

### Page 4: Human Review

**Purpose**: Expert review and approval of AI diagnoses.

**Features**:
- Display original AI diagnosis (preserved)
- Review decision selection:
  - ACCEPT
  - EDIT
  - REJECT
- Reviewer notes input
- Reason for correction (if EDIT/REJECT)
- Corrected diagnosis JSON editor (if EDIT)
- Save review button

**Review Workflow**:
1. Expert reviews AI diagnosis
2. Selects decision (ACCEPT/EDIT/REJECT)
3. Provides notes and reasoning
4. Corrects diagnosis if needed
5. Saves review with metadata

**Session State**:
- `review_decision`: Selected review decision
- `reviewer_notes`: Expert feedback
- `corrected_diagnosis`: Modified diagnosis
- `review_saved`: Whether review has been saved

### Page 5: Verification

**Purpose**: Track fix verification in Packet Tracer.

**Features**:
- Display final diagnosis (after review)
- Verification status selection:
  - VERIFIED
  - NOT VERIFIED
  - NOT YET TESTED
- Verification notes input
- Save verification button

**Verification Workflow**:
1. Expert applies fix in Packet Tracer
2. Records verification status
3. Provides verification notes
4. Saves verification result

**Session State**:
- `verification_status`: Verification status
- `verification_notes`: Verification feedback
- `verification_saved`: Whether verification has been saved

### Page 6: Responsible AI

**Purpose**: Display AI performance and accountability metrics.

**Features**:
- AI review distribution chart (Accepted/Edited/Rejected)
- AI-vs-human agreement rate
- Number of corrected AI diagnoses
- Cases with insufficient evidence
- AI performance over time
- Responsible AI evidence links

**Metrics Displayed**:
- Total reviews
- Accepted count
- Edited count
- Rejected count
- Agreement rate percentage
- Corrected case list

**Data Sources**:
- Review manager database
- Analytics metrics calculations
- Responsible AI evidence documents

### Page 7: Analytics Dashboard

**Purpose**: Comprehensive system performance insights.

**Features**:
- Total cases metric
- Cases by issue type chart
- Cases by severity chart
- AI review distribution chart
- AI-vs-human agreement rate
- Corrected diagnosis count
- Insufficient evidence count
- OSI layer distribution chart
- Rule checker findings by category

**Visualization**:
- Interactive Plotly charts
- Metric cards with counts
- Tables for detailed data
- Color-coded severity levels

**Methodology**:
- Uses only real stored project data
- Calculates metrics from actual review data
- Human review as source for agreement calculations
- Distinguishes AI prediction from human-reviewed result

## Session State Management

The dashboard uses Streamlit session state to maintain state across pages:

```python
# Data
st.session_state.cases = load_cases()
st.session_state.selected_case = None
st.session_state.developer_mode = False

# Rule Checker
st.session_state.rule_results = None
st.session_state.rule_checks_run = False

# AI Diagnosis
st.session_state.ai_diagnosis = None
st.session_state.ai_error = None
st.session_state.ai_diagnosis_run = False

# Human Review
st.session_state.review_decision = None
st.session_state.reviewer_notes = None
st.session_state.corrected_diagnosis = None
st.session_state.review_saved = False

# Verification
st.session_state.verification_status = None
st.session_state.verification_notes = None
st.session_state.verification_saved = False

# Review Manager
st.session_state.review_manager = ReviewManager()
```

## Navigation

The dashboard uses a sidebar for navigation:

```python
with st.sidebar:
    st.title("NetSage AI")
    
    page = st.radio(
        "Navigate",
        [
            "Case Selection",
            "Rule Checks",
            "AI Diagnosis",
            "Human Review",
            "Verification",
            "Responsible AI",
            "Analytics Dashboard"
        ]
    )
```

## Integration with Backend

### Data Loader Integration

```python
from data.data_loader import load_cases

st.session_state.cases = load_cases()
```

### Rule Checker Integration

```python
from rules.checker import run_all_checks

st.session_state.rule_results = run_all_checks(st.session_state.selected_case)
```

### AI Diagnosis Integration

```python
from ai.diagnose import diagnose_case

st.session_state.ai_diagnosis = diagnose_case(
    st.session_state.selected_case,
    st.session_state.rule_results
)
```

### Review Manager Integration

```python
from review.review_manager import ReviewManager
from review.schemas import ReviewDecision

st.session_state.review_manager.create_review(
    case_id=st.session_state.selected_case["case_id"],
    ai_diagnosis=st.session_state.ai_diagnosis,
    reviewer_decision=ReviewDecision(st.session_state.review_decision),
    ...
)
```

### Analytics Integration

```python
from analytics.metrics import (
    calculate_total_cases,
    calculate_cases_by_issue_type,
    calculate_ai_review_distribution,
    calculate_ai_agreement_rate,
    ...
)

total_cases = calculate_total_cases()
issue_types = calculate_cases_by_issue_type()
agreement_rate = calculate_ai_agreement_rate()
```

## Security Features

### API Key Protection

- API keys stored in environment variables only
- Never displayed in UI
- Streamlit config prevents exposure
- .env.example provided (no real keys)

### No Automatic Execution

- Fix steps displayed but not executed
- Manual verification required
- No network device configuration changes
- Clear separation of recommendation and action

### Developer Mode

- Expected fault hidden by default
- Toggle for evaluator testing
- Prevents bias in normal use
- Clear when active

## User Experience

### Loading States

- Loading indicators during AI diagnosis
- Progress indicators for batch operations
- Clear error messages
- Graceful degradation when AI unavailable

### Error Handling

- Friendly error messages
- Recovery suggestions
- No application crashes
- Clear next steps

### Clear Labels

- Descriptive button labels
- Clear section headers
- Metric explanations
- Tooltips for complex features

## Responsive Design

The dashboard adapts to different screen sizes:

- Mobile-friendly layout
- Responsive charts
- Collapsible sidebar
- Scrollable content areas

## Testing

### Dashboard Tests

```python
# test_dashboard.py
def test_all_required_pages_present():
    """Verify all 7 pages are implemented."""
    # Check for page markers in app.py
    pass

def test_no_api_key_exposure():
    """Verify API keys are not exposed in UI."""
    # Search for api_key in displayed elements
    pass

def test_human_review_enforcement():
    """Verify human review is required."""
    # Check for review workflow
    pass
```

### Running Dashboard Tests

```bash
pytest tests/test_dashboard.py
```

## Current Implementation Status

### Implemented Features

- ✅ All 7 pages implemented
- ✅ Session state management
- ✅ Backend integration (data, rules, AI, review, analytics)
- ✅ Security features (API key protection, no auto-execution)
- ✅ Error handling
- ✅ Responsive design
- ✅ Developer mode
- ✅ Interactive charts

### Current Limitations

- ⚠️ AI diagnosis requires API access
- ⚠️ No real review data (no AI diagnoses generated)
- ⚠️ Agreement rate displays N/A (no reviews)
- ✅ All infrastructure ready for full functionality

## Usage Example

### Typical Workflow

1. **Launch Dashboard**:
   ```bash
   streamlit run dashboard/app.py
   ```

2. **Select Case**:
   - Navigate to "Case Selection"
   - Select case from dropdown (e.g., NET-001)
   - Review case information

3. **Run Rule Checks**:
   - Navigate to "Rule Checks"
   - Click "Run Rule Checks"
   - Review deterministic findings

4. **Run AI Diagnosis**:
   - Navigate to "AI Diagnosis"
   - Click "Run AI Diagnosis"
   - Review AI diagnosis and evidence

5. **Human Review**:
   - Navigate to "Human Review"
   - Select decision (ACCEPT/EDIT/REJECT)
   - Provide notes and reasoning
   - Save review

6. **Verification**:
   - Navigate to "Verification"
   - Apply fix in Packet Tracer
   - Record verification status
   - Save verification

7. **View Analytics**:
   - Navigate to "Analytics Dashboard"
   - Review system performance metrics
   - Analyze AI performance

## Future Enhancements

### Potential Improvements

1. **Case Search**: Add search/filter for cases
2. **Batch Review**: Review multiple cases at once
3. **Comparison View**: Compare rule vs AI results side-by-side
4. **Export**: Export review data from dashboard
5. **Collaboration**: Share review notes with other experts
6. **Real-time Updates**: Live updates when reviews added

### Enhancement Strategy

Future enhancements should:
- Maintain security features
- Keep human review mandatory
- Preserve data integrity
- Improve user experience
- Support academic analysis

## Conclusion

The NetSage AI dashboard provides a comprehensive, user-friendly interface for network troubleshooting case analysis. It integrates all system components (data loader, rule checker, AI diagnosis, human review, analytics) into a unified workflow while maintaining security, enforcing human oversight, and providing valuable insights through interactive visualizations. The dashboard is fully functional and ready for complete operation when AI access is restored.