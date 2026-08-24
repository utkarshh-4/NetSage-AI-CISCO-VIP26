# Human Review Architecture

## Overview

The human review workflow is a critical component of the AI-powered network troubleshooting system. It ensures that AI diagnoses are reviewed by human experts before being considered final, maintaining safety and accuracy in network operations.

## Why Human Review is Required

### 1. **Safety and Risk Mitigation**
Network configuration changes can have significant operational impact. Incorrect diagnoses or fix recommendations could cause:
- Network outages
- Security vulnerabilities
- Performance degradation
- Service disruption

Human review provides a safety layer to prevent automated execution of potentially harmful changes.

### 2. **AI Limitations and Uncertainty**
AI models, even when well-trained, have limitations:
- May hallucinate evidence or configurations not present in the data
- May misinterpret ambiguous network evidence
- May lack context about the specific network environment
- Confidence levels may not always reflect true accuracy

Human reviewers can:
- Verify that the AI used only the provided evidence
- Correct misinterpretations
- Add context-specific knowledge
- Identify when evidence is truly insufficient

### 3. **Accountability and Auditability**
In network operations, accountability is essential:
- Every diagnosis must be traceable to a responsible party
- Changes must be documented with reasoning
- Historical records enable post-incident analysis
- Regulatory compliance may require human oversight

### 4. **Continuous Improvement**
Human review enables:
- Collection of corrected cases for model fine-tuning
- Identification of systematic AI weaknesses
- Improvement of deterministic rule checks
- Enhancement of prompt engineering

### 5. **Responsible AI Principles**
The system follows responsible AI practices:
- **Human-in-the-loop**: AI assists but does not replace human judgment
- **Transparency**: Original AI responses are preserved even when corrected
- **Explainability**: Reviewers must provide reasons for corrections/rejections
- **Fairness**: Human review prevents bias from being automatically applied

## Review Workflow

### 1. AI Diagnosis Generation
- Deterministic rule checker runs on case evidence
- AI diagnosis engine generates structured diagnosis
- Response includes: root_cause, confidence, evidence, fix_steps, etc.

### 2. Human Review
Reviewer evaluates the AI diagnosis and chooses one of three decisions:

#### ACCEPTED
- AI diagnosis is correct and complete
- No changes needed
- Final diagnosis = AI diagnosis
- AI-human agreement = True

#### EDITED
- AI diagnosis is partially correct but needs modification
- Reviewer provides corrected diagnosis
- Original AI response is preserved for comparison
- Final diagnosis = Corrected diagnosis
- AI-human agreement = False

#### REJECTED
- AI diagnosis is incorrect or based on insufficient evidence
- Reviewer may provide alternative diagnosis or reject entirely
- Original AI response is preserved
- Final diagnosis = AI diagnosis (for reference)
- AI-human agreement = False

### 3. Record Keeping
Each review records:
- `case_id`: Unique identifier
- `timestamp`: When review occurred
- `ai_diagnosis`: Original AI response (immutable)
- `reviewer_decision`: ACCEPTED/EDITED/REJECTED
- `corrected_diagnosis`: Human-corrected version (if edited)
- `reviewer_notes`: Reviewer's comments
- `reason_for_correction`: Explanation of why correction/rejection occurred
- `final_diagnosis`: Diagnosis after review
- `ai_human_agreed`: Whether AI and human agreed

### 4. Never Auto-Execute
The system enforces:
- No automatic execution of recommended fix steps
- All changes require explicit human approval
- Fix steps are recommendations only, not commands to be run
- Human must verify and execute fixes manually

## Data Model

### ReviewRecord
```python
class ReviewRecord:
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

### ReviewSummary
```python
class ReviewSummary:
    total_reviews: int
    accepted_count: int
    edited_count: int
    rejected_count: int
    agreement_rate: float
    corrected_cases: List[str]
```

## Persistence

### JSON Storage
- Primary storage in `data/reviews.json`
- Enables easy programmatic access
- Preserves full data structure
- Supports version control

### CSV Export
- Export capability to `data/reviews_export.csv`
- Enables analysis in spreadsheet tools
- Facilitates reporting and auditing
- Contains all review fields

## Responsible AI Requirements

The project requires at least 5 cases where the AI answer was corrected by a human. These cases:
- Are easily identifiable via `get_corrected_case_ids()`
- Can be exported for analysis
- Provide data for model improvement
- Demonstrate the value of human review

## Key Principles

1. **Preserve Original AI Response**: Even when corrected, the original AI diagnosis is never modified or deleted. This enables comparison and learning.

2. **Explicit Reasoning**: Reviewers must provide reasons for corrections or rejections. This transparency aids in understanding AI weaknesses.

3. **No Silent Corrections**: All corrections are explicitly recorded with the reviewer's identity (timestamp serves as proxy) and reasoning.

4. **Agreement Tracking**: The system tracks AI-human agreement rates to measure AI performance over time.

5. **Exportability**: Corrected cases can be easily exported for analysis, model fine-tuning, or reporting.

## Implementation

The review system is implemented in:
- `review/schemas.py`: Pydantic data models
- `review/review_manager.py`: CRUD operations and persistence
- `tests/test_review.py`: Comprehensive test coverage

## Testing

Tests cover:
- Creating accepted, edited, and rejected reviews
- Retrieving reviews by decision type
- Updating existing reviews
- Deleting reviews
- Agreement rate calculation
- Persistence across manager instances
- CSV export functionality
- Identification of corrected cases
