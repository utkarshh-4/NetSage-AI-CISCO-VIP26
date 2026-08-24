"""Review data model for human review workflow."""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class ReviewDecision(str, Enum):
    """Human review decision types."""
    ACCEPTED = "ACCEPTED"
    EDITED = "EDITED"
    REJECTED = "REJECTED"


class ReviewRecord(BaseModel):
    """Record of a human review for an AI diagnosis."""
    
    case_id: str = Field(..., description="ID of the case being reviewed")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp of the review")
    ai_diagnosis: Dict[str, Any] = Field(..., description="Original AI diagnosis response")
    reviewer_decision: ReviewDecision = Field(..., description="Reviewer's decision")
    corrected_diagnosis: Optional[Dict[str, Any]] = Field(None, description="Corrected diagnosis if edited")
    reviewer_notes: Optional[str] = Field(None, description="Reviewer's notes")
    reason_for_correction: Optional[str] = Field(None, description="Reason for correction/rejection")
    final_diagnosis: Dict[str, Any] = Field(..., description="Final diagnosis after review")
    ai_human_agreed: bool = Field(..., description="Whether AI and human agreed")
    
    def is_corrected(self) -> bool:
        """Check if this review resulted in a correction."""
        return self.reviewer_decision == ReviewDecision.EDITED
    
    def is_rejected(self) -> bool:
        """Check if this review resulted in rejection."""
        return self.reviewer_decision == ReviewDecision.REJECTED
    
    def is_accepted(self) -> bool:
        """Check if this review was accepted without changes."""
        return self.reviewer_decision == ReviewDecision.ACCEPTED


class ReviewSummary(BaseModel):
    """Summary statistics for review records."""
    
    total_reviews: int = Field(..., description="Total number of reviews")
    accepted_count: int = Field(..., description="Number of accepted reviews")
    edited_count: int = Field(..., description="Number of edited reviews")
    rejected_count: int = Field(..., description="Number of rejected reviews")
    agreement_rate: float = Field(..., description="Rate of AI-human agreement")
    corrected_cases: List[str] = Field(default_factory=list, description="List of case IDs that were corrected")
    
    def get_corrected_case_ids(self) -> List[str]:
        """Get list of case IDs that were corrected."""
        return self.corrected_cases
