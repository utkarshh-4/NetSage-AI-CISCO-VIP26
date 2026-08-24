"""Tests for AI schema validation."""

import pytest
from ai.schemas import (
    DiagnosisResponse, EvidenceItem, FixStep, AlternativeCause,
    DiagnosisError, ConfidenceLevel, SeverityLevel, OSILayer
)
from pydantic import ValidationError


class TestEvidenceItem:
    """Test suite for EvidenceItem schema."""
    
    def test_valid_evidence_item(self):
        """Test creating a valid evidence item."""
        evidence = EvidenceItem(
            source="show ip interface",
            content="GigabitEthernet0/0 is up",
            type="observed"
        )
        assert evidence.source == "show ip interface"
        assert evidence.content == "GigabitEthernet0/0 is up"
        assert evidence.type == "observed"
    
    def test_missing_required_field(self):
        """Test that missing required fields raise ValidationError."""
        with pytest.raises(ValidationError):
            EvidenceItem(source="test", content="test")
            # type is required


class TestFixStep:
    """Test suite for FixStep schema."""
    
    def test_valid_fix_step(self):
        """Test creating a valid fix step."""
        step = FixStep(
            step_number=1,
            command="interface GigabitEthernet0/0",
            explanation="Enter interface configuration mode",
            verification="show ip interface brief"
        )
        assert step.step_number == 1
        assert step.command == "interface GigabitEthernet0/0"
    
    def test_step_number_must_be_positive(self):
        """Test that step_number must be >= 1."""
        with pytest.raises(ValidationError):
            FixStep(
                step_number=0,
                command="test",
                explanation="test"
            )
    
    def test_verification_is_optional(self):
        """Test that verification field is optional."""
        step = FixStep(
            step_number=1,
            command="test",
            explanation="test"
        )
        assert step.verification is None


class TestAlternativeCause:
    """Test suite for AlternativeCause schema."""
    
    def test_valid_alternative_cause(self):
        """Test creating a valid alternative cause."""
        cause = AlternativeCause(
            description="Possible cable fault",
            likelihood="medium",
            evidence=["Physical layer issues"]
        )
        assert cause.description == "Possible cable fault"
        assert cause.likelihood == "medium"
    
    def test_evidence_defaults_to_empty_list(self):
        """Test that evidence defaults to empty list."""
        cause = AlternativeCause(
            description="Test",
            likelihood="low"
        )
        assert cause.evidence == []


class TestDiagnosisResponse:
    """Test suite for DiagnosisResponse schema."""
    
    def test_valid_diagnosis_response(self):
        """Test creating a valid diagnosis response."""
        response = DiagnosisResponse(
            root_cause="Interface is administratively down",
            confidence=ConfidenceLevel.HIGH,
            evidence=[
                EvidenceItem(
                    source="show_outputs",
                    content="administratively down",
                    type="observed"
                )
            ],
            osi_layer=OSILayer.NETWORK,
            issue_type="routing",
            severity=SeverityLevel.HIGH
        )
        assert response.root_cause == "Interface is administratively down"
        assert response.confidence == ConfidenceLevel.HIGH
        assert len(response.evidence) == 1
        assert response.requires_human_review is True  # default
    
    def test_evidence_must_not_be_empty(self):
        """Test that evidence list cannot be empty."""
        with pytest.raises(ValidationError):
            DiagnosisResponse(
                root_cause="Test",
                confidence=ConfidenceLevel.HIGH,
                evidence=[],
                osi_layer=OSILayer.NETWORK,
                issue_type="routing",
                severity=SeverityLevel.HIGH
            )
    
    def test_fix_steps_must_be_sequential(self):
        """Test that fix steps must be in sequential order."""
        with pytest.raises(ValidationError):
            DiagnosisResponse(
                root_cause="Test",
                confidence=ConfidenceLevel.HIGH,
                evidence=[
                    EvidenceItem(
                        source="test",
                        content="test",
                        type="observed"
                    )
                ],
                fix_steps=[
                    FixStep(step_number=2, command="test", explanation="test"),
                    FixStep(step_number=1, command="test", explanation="test")
                ],
                osi_layer=OSILayer.NETWORK,
                issue_type="routing",
                severity=SeverityLevel.HIGH
            )
    
    def test_fix_steps_must_start_at_1(self):
        """Test that fix steps must start at 1."""
        with pytest.raises(ValidationError):
            DiagnosisResponse(
                root_cause="Test",
                confidence=ConfidenceLevel.HIGH,
                evidence=[
                    EvidenceItem(
                        source="test",
                        content="test",
                        type="observed"
                    )
                ],
                fix_steps=[
                    FixStep(step_number=2, command="test", explanation="test"),
                    FixStep(step_number=3, command="test", explanation="test")
                ],
                osi_layer=OSILayer.NETWORK,
                issue_type="routing",
                severity=SeverityLevel.HIGH
            )
    
    def test_fix_steps_must_be_consecutive(self):
        """Test that fix steps must be consecutive."""
        with pytest.raises(ValidationError):
            DiagnosisResponse(
                root_cause="Test",
                confidence=ConfidenceLevel.HIGH,
                evidence=[
                    EvidenceItem(
                        source="test",
                        content="test",
                        type="observed"
                    )
                ],
                fix_steps=[
                    FixStep(step_number=1, command="test", explanation="test"),
                    FixStep(step_number=3, command="test", explanation="test")
                ],
                osi_layer=OSILayer.NETWORK,
                issue_type="routing",
                severity=SeverityLevel.HIGH
            )
    
    def test_next_command_must_not_be_empty_string(self):
        """Test that next_command cannot be empty string if provided."""
        with pytest.raises(ValidationError):
            DiagnosisResponse(
                root_cause="Test",
                confidence=ConfidenceLevel.HIGH,
                evidence=[
                    EvidenceItem(
                        source="test",
                        content="test",
                        type="observed"
                    )
                ],
                next_command="",
                osi_layer=OSILayer.NETWORK,
                issue_type="routing",
                severity=SeverityLevel.HIGH
            )
    
    def test_next_command_can_be_none(self):
        """Test that next_command can be None."""
        response = DiagnosisResponse(
            root_cause="Test",
            confidence=ConfidenceLevel.HIGH,
            evidence=[
                EvidenceItem(
                    source="test",
                    content="test",
                    type="observed"
                )
            ],
            next_command=None,
            osi_layer=OSILayer.NETWORK,
            issue_type="routing",
            severity=SeverityLevel.HIGH
        )
        assert response.next_command is None
    
    def test_full_diagnosis_response(self):
        """Test creating a complete diagnosis response with all fields."""
        response = DiagnosisResponse(
            root_cause="Router sub-interface is administratively down",
            confidence=ConfidenceLevel.HIGH,
            evidence=[
                EvidenceItem(
                    source="show_outputs",
                    content="GigabitEthernet0/0.10 is administratively down",
                    type="observed"
                ),
                EvidenceItem(
                    source="rule_checker",
                    content="interface_down check detected",
                    type="observed"
                )
            ],
            next_command=None,
            fix_steps=[
                FixStep(
                    step_number=1,
                    command="interface GigabitEthernet0/0.10",
                    explanation="Enter sub-interface configuration mode",
                    verification="show ip interface brief"
                ),
                FixStep(
                    step_number=2,
                    command="no shutdown",
                    explanation="Enable the sub-interface",
                    verification="Verify interface status is up"
                )
            ],
            osi_layer=OSILayer.NETWORK,
            issue_type="routing",
            severity=SeverityLevel.HIGH,
            alternative_causes=[
                AlternativeCause(
                    description="Intentional maintenance shutdown",
                    likelihood="low",
                    evidence=["No maintenance schedule provided"]
                )
            ],
            limitations=["Cannot verify if shutdown is intentional"],
            notes="Requires human verification",
            requires_human_review=True
        )
        
        assert len(response.evidence) == 2
        assert len(response.fix_steps) == 2
        assert len(response.alternative_causes) == 1
        assert len(response.limitations) == 1
        assert response.requires_human_review is True


class TestDiagnosisError:
    """Test suite for DiagnosisError schema."""
    
    def test_valid_diagnosis_error(self):
        """Test creating a valid diagnosis error."""
        error = DiagnosisError(
            error_type="api_error",
            message="OpenAI API returned an error",
            details={"status_code": 500},
            retry_possible=True
        )
        assert error.error_type == "api_error"
        assert error.retry_possible is True
    
    def test_defaults(self):
        """Test default values for optional fields."""
        error = DiagnosisError(
            error_type="test_error",
            message="Test message"
        )
        assert error.details is None
        assert error.retry_possible is True  # default


class TestEnums:
    """Test suite for enum types."""
    
    def test_confidence_levels(self):
        """Test confidence level enum values."""
        assert ConfidenceLevel.HIGH == "high"
        assert ConfidenceLevel.MEDIUM == "medium"
        assert ConfidenceLevel.LOW == "low"
    
    def test_severity_levels(self):
        """Test severity level enum values."""
        assert SeverityLevel.HIGH == "high"
        assert SeverityLevel.MEDIUM == "medium"
        assert SeverityLevel.LOW == "low"
    
    def test_osi_layers(self):
        """Test OSI layer enum values."""
        assert OSILayer.PHYSICAL == "Layer 1"
        assert OSILayer.DATALINK == "Layer 2"
        assert OSILayer.NETWORK == "Layer 3"
        assert OSILayer.TRANSPORT == "Layer 4"
        assert OSILayer.SESSION == "Layer 5"
        assert OSILayer.PRESENTATION == "Layer 6"
        assert OSILayer.APPLICATION == "Layer 7"
