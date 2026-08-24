"""Pydantic schemas for AI diagnosis responses."""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from enum import Enum


class ConfidenceLevel(str, Enum):
    """Confidence levels for AI diagnosis."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class SeverityLevel(str, Enum):
    """Severity levels for issues."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class OSILayer(str, Enum):
    """OSI layer classification."""
    PHYSICAL = "Layer 1"
    DATALINK = "Layer 2"
    NETWORK = "Layer 3"
    TRANSPORT = "Layer 4"
    SESSION = "Layer 5"
    PRESENTATION = "Layer 6"
    APPLICATION = "Layer 7"


class EvidenceItem(BaseModel):
    """Single piece of evidence."""
    source: str = Field(..., description="Source of evidence (e.g., 'show ip interface', 'log message')")
    content: str = Field(..., description="Actual evidence content")
    type: str = Field(..., description="Type of evidence (e.g., 'observed', 'inferred')")


class FixStep(BaseModel):
    """Single fix step."""
    step_number: int = Field(..., ge=1, description="Step number in sequence")
    command: str = Field(..., description="Command to execute")
    explanation: str = Field(..., description="Explanation of what this step does")
    verification: Optional[str] = Field(None, description="How to verify the fix was successful")


class AlternativeCause(BaseModel):
    """Alternative possible cause."""
    description: str = Field(..., description="Description of alternative cause")
    likelihood: str = Field(..., description="Likelihood (high/medium/low)")
    evidence: List[str] = Field(default_factory=list, description="Evidence supporting this alternative")


class DiagnosisResponse(BaseModel):
    """Structured AI diagnosis response."""
    
    # Required fields from project brief
    root_cause: str = Field(..., description="Primary root cause of the issue")
    confidence: ConfidenceLevel = Field(..., description="Confidence in diagnosis")
    evidence: List[EvidenceItem] = Field(..., description="Evidence supporting diagnosis")
    next_command: Optional[str] = Field(None, description="Next diagnostic command to run")
    fix_steps: List[FixStep] = Field(default_factory=list, description="Steps to fix the issue")
    
    # Additional required fields
    osi_layer: OSILayer = Field(..., description="OSI layer where issue occurs")
    issue_type: str = Field(..., description="Type of issue (e.g., 'routing', 'switching', 'addressing')")
    severity: SeverityLevel = Field(..., description="Severity of the issue")
    alternative_causes: List[AlternativeCause] = Field(default_factory=list, description="Alternative possible causes")
    limitations: List[str] = Field(default_factory=list, description="Limitations of the diagnosis")
    
    # Optional fields
    notes: Optional[str] = Field(None, description="Additional notes or context")
    requires_human_review: bool = Field(default=True, description="Whether human review is required")
    
    @field_validator('fix_steps')
    @classmethod
    def fix_steps_must_be_sequential(cls, v: List[FixStep]) -> List[FixStep]:
        """Validate that fix steps are sequential."""
        if v:
            step_numbers = [step.step_number for step in v]
            if step_numbers != sorted(step_numbers):
                raise ValueError("Fix steps must be in sequential order")
            if step_numbers != list(range(1, len(v) + 1)):
                raise ValueError("Fix steps must start at 1 and be consecutive")
        return v
    
    @field_validator('evidence')
    @classmethod
    def evidence_must_not_be_empty(cls, v: List[EvidenceItem]) -> List[EvidenceItem]:
        """Validate that at least one evidence item is provided."""
        if not v:
            raise ValueError("At least one evidence item must be provided")
        return v
    
    @field_validator('next_command')
    @classmethod
    def next_command_must_be_valid_if_provided(cls, v: Optional[str]) -> Optional[str]:
        """Validate next_command format if provided."""
        if v is not None and not v.strip():
            raise ValueError("next_command must not be empty if provided")
        return v


class DiagnosisError(BaseModel):
    """Error response when diagnosis fails."""
    error_type: str = Field(..., description="Type of error (e.g., 'api_error', 'validation_error')")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    retry_possible: bool = Field(default=True, description="Whether the operation can be retried")
