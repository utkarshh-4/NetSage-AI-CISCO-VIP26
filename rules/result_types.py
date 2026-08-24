"""Result types for rule checks."""

from typing import Dict, List, Any


class CheckResult:
    """Normalized result format for rule checks."""
    
    def __init__(
        self,
        check_name: str,
        status: str,
        severity: str = "medium",
        message: str = "",
        evidence: List[str] = None,
        confidence: str = "medium"
    ):
        """
        Initialize a check result.
        
        Args:
            check_name: Name of the check performed
            status: One of DETECTED, NOT_DETECTED, INSUFFICIENT_EVIDENCE, ERROR
            severity: Severity level (high, medium, low)
            message: Human-readable message
            evidence: List of evidence strings
            confidence: Confidence level (high, medium, low)
        """
        valid_statuses = ["DETECTED", "NOT_DETECTED", "INSUFFICIENT_EVIDENCE", "ERROR"]
        if status not in valid_statuses:
            raise ValueError(f"Invalid status: {status}. Must be one of {valid_statuses}")
        
        self.check_name = check_name
        self.status = status
        self.severity = severity
        self.message = message
        self.evidence = evidence or []
        self.confidence = confidence
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "check_name": self.check_name,
            "status": self.status,
            "severity": self.severity,
            "message": self.message,
            "evidence": self.evidence,
            "confidence": self.confidence
        }
    
    def __repr__(self) -> str:
        return f"CheckResult({self.check_name}: {self.status})"
