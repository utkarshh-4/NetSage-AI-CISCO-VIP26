# Human Review Explanation

## Overview

The human review system is a critical component of NetSage AI that ensures expert oversight of AI-generated diagnoses. It provides a structured workflow for network experts to review, validate, and correct AI recommendations before any action is taken.

## Purpose

The human review system serves to:

1. **Expert Oversight**: Ensure AI diagnoses are reviewed by qualified network experts
2. **Quality Control**: Validate AI accuracy and identify errors
3. **Learning**: Capture expert corrections to improve understanding
4. **Accountability**: Maintain audit trail of human-AI interactions
5. **Responsible AI**: Demonstrate responsible AI deployment with human oversight

## Architecture

### Component Structure

```
review/
├── review_manager.py    # Review workflow management
└── schemas.py          # Review data models
```

### Review Manager (`review_manager.py`)

The review manager coordinates the entire review workflow:

- Create reviews (ACCEPT/EDIT/REJECT)
- Store review metadata
- Calculate agreement statistics
- Export review data
- Maintain review history

### Review Schema (`schemas.py`)

Defines the data structures for reviews:

```python
class ReviewDecision(str, Enum):
    ACCEPTED = "ACCEPTED"
    EDITED = "EDITED"
    REJECTED = "REJECTED"

class ReviewRecord(BaseModel):
    case_id: str
    timestamp: datetime
    ai_diagnosis: Dict[str, Any]
    reviewer_decision: ReviewDecision
    corrected_diagnosis: Optional[Dict[str, Any]]
    reviewer_notes: Optional[str]
    reason_for_correction: Optional[str]
    final_diagnosis: Dict[str, Any]
    ai_human_agreed: bool
```

## Review Workflow

### Step 1: AI Diagnosis Generated

The AI diagnosis system produces a structured diagnosis:

```json
{
  "root_cause": "Router sub-interface Gi0/0.10 is administratively shutdown",
  "confidence": "high",
  "evidence": [...],
  "fix_steps": [...],
  "requires_human_review": true
}
```

### Step 2: Expert Review

Network expert reviews the AI diagnosis in the Streamlit interface:

**Review Interface Shows**:
- Original AI diagnosis (preserved)
- Case data (symptom, topology, show outputs)
- Rule checker results
- AI confidence level
- Proposed fix steps

### Step 3: Decision

Expert selects one of three decisions:

#### ACCEPTED
- AI diagnosis is correct as-is
- No changes needed
- AI diagnosis becomes final diagnosis

**Use Case**: AI correctly identifies the issue with appropriate confidence and evidence.

#### EDITED
- AI diagnosis needs correction
- Expert modifies the diagnosis JSON
- Corrected diagnosis becomes final diagnosis

**Use Case**: AI identifies the issue but has incorrect details, confidence level, or fix steps.

#### REJECTED
- AI diagnosis is incorrect
- AI diagnosis is discarded
- Expert provides manual diagnosis (optional)

**Use Case**: AI misidentifies the issue or provides harmful recommendations.

### Step 4: Review Documentation

Expert provides:

**Reviewer Notes**:
- Why the decision was made
- Specific corrections (if edited)
- Additional context

**Reason for Correction** (if edited/rejected):
- Why AI was wrong
- What evidence was misinterpreted
- Correct analysis

### Step 5: Final Diagnosis

System determines final diagnosis:

```python
if decision == ACCEPTED:
    final_diagnosis = ai_diagnosis
    ai_human_agreed = True
elif decision == EDITED:
    final_diagnosis = corrected_diagnosis
    ai_human_agreed = False
elif decision == REJECTED:
    final_diagnosis = manual_diagnosis (if provided)
    ai_human_agreed = False
```

### Step 6: Metrics Update

System updates analytics:

- AI review distribution (Accepted/Edited/Rejected counts)
- AI-human agreement rate
- Corrected diagnosis count
- Review history

## Review Data Model

### ReviewRecord

```python
class ReviewRecord(BaseModel):
    """Record of a human review for an AI diagnosis."""
    
    case_id: str
    """ID of the case being reviewed"""
    
    timestamp: datetime
    """Timestamp of the review"""
    
    ai_diagnosis: Dict[str, Any]
    """Original AI diagnosis response (preserved)"""
    
    reviewer_decision: ReviewDecision
    """Reviewer's decision (ACCEPTED/EDITED/REJECTED)"""
    
    corrected_diagnosis: Optional[Dict[str, Any]]
    """Corrected diagnosis if edited"""
    
    reviewer_notes: Optional[str]
    """Reviewer's notes and feedback"""
    
    reason_for_correction: Optional[str]
    """Reason for correction/rejection"""
    
    final_diagnosis: Dict[str, Any]
    """Final diagnosis after review"""
    
    ai_human_agreed: bool
    """Whether AI and human agreed"""
```

### ReviewDecision Enum

```python
class ReviewDecision(str, Enum):
    """Human review decision types."""
    
    ACCEPTED = "ACCEPTED"
    """AI diagnosis correct as-is"""
    
    EDITED = "EDITED"
    """AI diagnosis needs correction"""
    
    REJECTED = "REJECTED"
    """AI diagnosis incorrect"""
```

## Agreement Calculation

### Agreement Rate

The system calculates AI-human agreement rate:

```python
agreement_rate = accepted_count / total_reviews
```

**Example**:
- Total reviews: 30
- Accepted: 24
- Edited: 4
- Rejected: 2
- Agreement rate: 24/30 = 80%

### Agreement Metrics

- **Accepted Count**: Number of reviews where AI was correct
- **Edited Count**: Number of reviews where AI needed correction
- **Rejected Count**: Number of reviews where AI was incorrect
- **Agreement Rate**: Percentage of accepted reviews
- **Corrected Cases**: List of case IDs that were edited or rejected

## Usage Examples

### Create Accepted Review

```python
from review.review_manager import ReviewManager
from review.schemas import ReviewDecision

review_manager = ReviewManager()

# Load AI diagnosis
ai_diagnosis = {...}  # from AI system

# Create accepted review
review = review_manager.create_review(
    case_id="NET-001",
    ai_diagnosis=ai_diagnosis,
    reviewer_decision=ReviewDecision.ACCEPTED,
    reviewer_notes="AI correctly identified interface down issue",
    final_diagnosis=ai_diagnosis
)
```

### Create Edited Review

```python
# Create edited review with corrections
corrected_diagnosis = ai_diagnosis.copy()
corrected_diagnosis["root_cause"] = "Corrected root cause"
corrected_diagnosis["confidence"] = "medium"

review = review_manager.create_review(
    case_id="NET-002",
    ai_diagnosis=ai_diagnosis,
    reviewer_decision=ReviewDecision.EDITED,
    corrected_diagnosis=corrected_diagnosis,
    reviewer_notes="AI missed the DHCP scope exhaustion",
    reason_for_correction="AI focused on wrong symptom",
    final_diagnosis=corrected_diagnosis
)
```

### Create Rejected Review

```python
# Create rejected review
review = review_manager.create_review(
    case_id="NET-003",
    ai_diagnosis=ai_diagnosis,
    reviewer_decision=ReviewDecision.REJECTED,
    reviewer_notes="AI misidentified the issue completely",
    reason_for_correction="AI hallucinated evidence not present in case",
    final_diagnosis=manual_diagnosis
)
```

### Calculate Agreement Rate

```python
from review.review_manager import ReviewManager

review_manager = ReviewManager()
all_reviews = review_manager.get_all_reviews()

summary = review_manager.get_summary()
print(f"Agreement rate: {summary.agreement_rate:.2%}")
print(f"Accepted: {summary.accepted_count}")
print(f"Edited: {summary.edited_count}")
print(f"Rejected: {summary.rejected_count}")
```

## Integration with Streamlit

### Human Review Page

The Streamlit dashboard provides a dedicated Human Review page:

```python
# In dashboard/app.py
if st.session_state.current_page == "Human Review":
    st.header("Human Review")
    
    # Display AI diagnosis
    st.json(st.session_state.ai_diagnosis)
    
    # Review decision
    decision = st.selectbox(
        "Review Decision",
        ["ACCEPT", "EDIT", "REJECT"]
    )
    
    # Reviewer notes
    notes = st.text_area("Reviewer Notes")
    
    # Reason for correction (if edited/rejected)
    if decision in ["EDIT", "REJECT"]:
        reason = st.text_area("Reason for Correction")
    
    # Save review
    if st.button("Save Review"):
        review_manager.create_review(...)
        st.success("Review saved successfully")
```

## Responsible AI Compliance

### Original AI Preservation

The system always preserves the original AI diagnosis:

```python
# Original AI is never modified
ai_diagnosis = {...}  # preserved as-is

# Corrections stored separately
corrected_diagnosis = {...}  # if edited
```

### Review Metadata

The system captures comprehensive metadata:

- Timestamp of review
- Reviewer decision
- Reviewer notes
- Reason for correction
- Agreement status

### Audit Trail

All reviews are stored and can be exported:

```python
# Export to CSV
review_manager.export_to_csv("reviews.csv")

# Get review history
all_reviews = review_manager.get_all_reviews()
```

## Current Implementation Status

### Infrastructure Status

- ✅ Review data models implemented
- ✅ Review manager functional
- ✅ Streamlit integration complete
- ✅ Agreement calculation working
- ✅ Export capabilities implemented
- ✅ Persistence layer functional

### Review Data Status

- ⚠️ Zero real reviews exist (no AI diagnoses generated)
- ⚠️ No real corrections to analyze (API quota limitation)
- ✅ System ready for reviews when AI access restored

### Phase 8 Status

From Phase 8 (Responsible AI Evidence):
- Zero real AI corrections documented
- Honest reporting of API limitations
- Infrastructure ready for full compliance

## Testing

### Unit Tests

```python
# test_review.py
def test_create_review_accepted():
    review = review_manager.create_review(
        case_id="NET-001",
        ai_diagnosis=test_diagnosis,
        reviewer_decision=ReviewDecision.ACCEPTED,
        ...
    )
    assert review.reviewer_decision == ReviewDecision.ACCEPTED
    assert review.ai_human_agreed == True
```

### Integration Tests

```python
def test_agreement_calculation():
    # Create multiple reviews
    review_manager.create_review(..., decision=ACCEPTED)
    review_manager.create_review(..., decision=EDITED)
    review_manager.create_review(..., decision=REJECTED)
    
    summary = review_manager.get_summary()
    assert summary.agreement_rate == 1/3
```

### Running Review Tests

```bash
pytest tests/test_review.py
```

## Best Practices

### For Reviewers

1. **Preserve Evidence**: Always reference actual case evidence
2. **Clear Notes**: Provide specific, actionable feedback
3. **Correct Diagnosis**: Ensure corrected diagnosis is accurate
4. **Reason Documentation**: Explain why corrections are needed
5. **Consistency**: Apply similar standards across reviews

### For System Design

1. **Original Preservation**: Never modify original AI diagnosis
2. **Metadata Capture**: Capture all relevant review metadata
3. **Agreement Tracking**: Calculate and report agreement rates
4. **Export Capability**: Allow review data export for analysis
5. **Audit Trail**: Maintain complete review history

## Future Enhancements

### Potential Improvements

1. **Reviewer Identification**: Track which expert performed each review
2. **Review Time**: Capture time spent on each review
3. **Correction Categories**: Classify types of corrections
4. **Reviewer Notes Analysis**: Analyze patterns in reviewer feedback
5. **Confidence Calibration**: Track confidence vs accuracy

### Enhancement Strategy

Future enhancements should:
- Maintain original AI preservation
- Keep human review mandatory
- Preserve audit trail
- Support academic analysis
- Improve reviewer experience

## Conclusion

The human review system is a critical component that ensures responsible AI deployment. By requiring expert oversight, preserving original AI diagnoses, and maintaining comprehensive metadata, the system demonstrates responsible AI practices while providing valuable learning opportunities from expert corrections. The infrastructure is fully implemented and ready for use when AI diagnoses are generated.