"""Tests for review manager and human review workflow."""

import pytest
import tempfile
import json
from pathlib import Path
from datetime import datetime

from review.schemas import ReviewRecord, ReviewDecision, ReviewSummary
from review.review_manager import ReviewManager


class TestReviewRecord:
    """Test suite for ReviewRecord schema."""
    
    def test_valid_review_record_accepted(self):
        """Test creating a valid accepted review record."""
        ai_diagnosis = {
            "root_cause": "Interface down",
            "confidence": "high",
            "evidence": [{"source": "test", "content": "test", "type": "observed"}],
            "osi_layer": "Layer 3",
            "issue_type": "routing",
            "severity": "high"
        }
        
        record = ReviewRecord(
            case_id="TEST-001",
            ai_diagnosis=ai_diagnosis,
            reviewer_decision=ReviewDecision.ACCEPTED,
            final_diagnosis=ai_diagnosis,
            ai_human_agreed=True
        )
        
        assert record.case_id == "TEST-001"
        assert record.reviewer_decision == ReviewDecision.ACCEPTED
        assert record.is_accepted()
        assert not record.is_corrected()
        assert not record.is_rejected()
    
    def test_valid_review_record_edited(self):
        """Test creating a valid edited review record."""
        ai_diagnosis = {
            "root_cause": "Interface down",
            "confidence": "high",
            "evidence": [{"source": "test", "content": "test", "type": "observed"}],
            "osi_layer": "Layer 3",
            "issue_type": "routing",
            "severity": "high"
        }
        
        corrected_diagnosis = {
            "root_cause": "Cable unplugged",
            "confidence": "high",
            "evidence": [{"source": "test", "content": "test", "type": "observed"}],
            "osi_layer": "Layer 1",
            "issue_type": "physical",
            "severity": "high"
        }
        
        record = ReviewRecord(
            case_id="TEST-001",
            ai_diagnosis=ai_diagnosis,
            reviewer_decision=ReviewDecision.EDITED,
            corrected_diagnosis=corrected_diagnosis,
            reviewer_notes="AI missed the physical layer issue",
            reason_for_correction="Evidence points to physical layer",
            final_diagnosis=corrected_diagnosis,
            ai_human_agreed=False
        )
        
        assert record.reviewer_decision == ReviewDecision.EDITED
        assert record.is_corrected()
        assert not record.is_accepted()
        assert not record.is_rejected()
        assert record.corrected_diagnosis == corrected_diagnosis
    
    def test_valid_review_record_rejected(self):
        """Test creating a valid rejected review record."""
        ai_diagnosis = {
            "root_cause": "Interface down",
            "confidence": "high",
            "evidence": [{"source": "test", "content": "test", "type": "observed"}],
            "osi_layer": "Layer 3",
            "issue_type": "routing",
            "severity": "high"
        }
        
        record = ReviewRecord(
            case_id="TEST-001",
            ai_diagnosis=ai_diagnosis,
            reviewer_decision=ReviewDecision.REJECTED,
            reviewer_notes="Insufficient evidence",
            reason_for_correction="Evidence is incomplete",
            final_diagnosis=ai_diagnosis,
            ai_human_agreed=False
        )
        
        assert record.reviewer_decision == ReviewDecision.REJECTED
        assert record.is_rejected()
        assert not record.is_accepted()
        assert not record.is_corrected()
    
    def test_timestamp_auto_generated(self):
        """Test that timestamp is auto-generated."""
        record = ReviewRecord(
            case_id="TEST-001",
            ai_diagnosis={"root_cause": "test"},
            reviewer_decision=ReviewDecision.ACCEPTED,
            final_diagnosis={"root_cause": "test"},
            ai_human_agreed=True
        )
        
        assert record.timestamp is not None
        assert isinstance(record.timestamp, datetime)


class TestReviewManager:
    """Test suite for ReviewManager."""
    
    @pytest.fixture
    def temp_storage(self):
        """Create a temporary storage file for testing."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        yield temp_path
        # Cleanup
        if Path(temp_path).exists():
            Path(temp_path).unlink()
    
    def test_create_review_accepted(self, temp_storage):
        """Test creating an accepted review."""
        manager = ReviewManager(temp_storage)
        
        ai_diagnosis = {
            "root_cause": "Interface down",
            "confidence": "high",
            "evidence": [{"source": "test", "content": "test", "type": "observed"}],
            "osi_layer": "Layer 3",
            "issue_type": "routing",
            "severity": "high"
        }
        
        record = manager.create_review(
            case_id="TEST-001",
            ai_diagnosis=ai_diagnosis,
            reviewer_decision=ReviewDecision.ACCEPTED
        )
        
        assert record.case_id == "TEST-001"
        assert record.is_accepted()
        assert record.ai_human_agreed is True
    
    def test_create_review_edited(self, temp_storage):
        """Test creating an edited review."""
        manager = ReviewManager(temp_storage)
        
        ai_diagnosis = {"root_cause": "test", "confidence": "high", "evidence": [], "osi_layer": "Layer 3", "issue_type": "test", "severity": "high"}
        corrected_diagnosis = {"root_cause": "corrected", "confidence": "high", "evidence": [], "osi_layer": "Layer 3", "issue_type": "test", "severity": "high"}
        
        record = manager.create_review(
            case_id="TEST-001",
            ai_diagnosis=ai_diagnosis,
            reviewer_decision=ReviewDecision.EDITED,
            corrected_diagnosis=corrected_diagnosis,
            reviewer_notes="Correction needed",
            reason_for_correction="AI was wrong"
        )
        
        assert record.is_corrected()
        assert record.ai_human_agreed is False
        assert record.corrected_diagnosis == corrected_diagnosis
    
    def test_create_review_rejected(self, temp_storage):
        """Test creating a rejected review."""
        manager = ReviewManager(temp_storage)
        
        ai_diagnosis = {"root_cause": "test", "confidence": "high", "evidence": [], "osi_layer": "Layer 3", "issue_type": "test", "severity": "high"}
        
        record = manager.create_review(
            case_id="TEST-001",
            ai_diagnosis=ai_diagnosis,
            reviewer_decision=ReviewDecision.REJECTED,
            reviewer_notes="Reject",
            reason_for_correction="Insufficient evidence"
        )
        
        assert record.is_rejected()
        assert record.ai_human_agreed is False
    
    def test_get_review(self, temp_storage):
        """Test getting a specific review."""
        manager = ReviewManager(temp_storage)
        
        ai_diagnosis = {"root_cause": "test", "confidence": "high", "evidence": [], "osi_layer": "Layer 3", "issue_type": "test", "severity": "high"}
        
        manager.create_review(
            case_id="TEST-001",
            ai_diagnosis=ai_diagnosis,
            reviewer_decision=ReviewDecision.ACCEPTED
        )
        
        record = manager.get_review("TEST-001")
        
        assert record is not None
        assert record.case_id == "TEST-001"
    
    def test_get_review_not_found(self, temp_storage):
        """Test getting a non-existent review."""
        manager = ReviewManager(temp_storage)
        
        record = manager.get_review("NONEXISTENT")
        
        assert record is None
    
    def test_get_all_reviews(self, temp_storage):
        """Test getting all reviews."""
        manager = ReviewManager(temp_storage)
        
        ai_diagnosis = {"root_cause": "test", "confidence": "high", "evidence": [], "osi_layer": "Layer 3", "issue_type": "test", "severity": "high"}
        
        manager.create_review("TEST-001", ai_diagnosis, ReviewDecision.ACCEPTED)
        manager.create_review("TEST-002", ai_diagnosis, ReviewDecision.EDITED)
        manager.create_review("TEST-003", ai_diagnosis, ReviewDecision.REJECTED)
        
        reviews = manager.get_all_reviews()
        
        assert len(reviews) == 3
    
    def test_get_corrected_reviews(self, temp_storage):
        """Test getting corrected reviews only."""
        manager = ReviewManager(temp_storage)
        
        ai_diagnosis = {"root_cause": "test", "confidence": "high", "evidence": [], "osi_layer": "Layer 3", "issue_type": "test", "severity": "high"}
        
        manager.create_review("TEST-001", ai_diagnosis, ReviewDecision.ACCEPTED)
        manager.create_review("TEST-002", ai_diagnosis, ReviewDecision.EDITED)
        manager.create_review("TEST-003", ai_diagnosis, ReviewDecision.EDITED)
        
        corrected = manager.get_corrected_reviews()
        
        assert len(corrected) == 2
        assert all(r.is_corrected() for r in corrected)
    
    def test_get_rejected_reviews(self, temp_storage):
        """Test getting rejected reviews only."""
        manager = ReviewManager(temp_storage)
        
        ai_diagnosis = {"root_cause": "test", "confidence": "high", "evidence": [], "osi_layer": "Layer 3", "issue_type": "test", "severity": "high"}
        
        manager.create_review("TEST-001", ai_diagnosis, ReviewDecision.ACCEPTED)
        manager.create_review("TEST-002", ai_diagnosis, ReviewDecision.REJECTED)
        manager.create_review("TEST-003", ai_diagnosis, ReviewDecision.REJECTED)
        
        rejected = manager.get_rejected_reviews()
        
        assert len(rejected) == 2
        assert all(r.is_rejected() for r in rejected)
    
    def test_get_accepted_reviews(self, temp_storage):
        """Test getting accepted reviews only."""
        manager = ReviewManager(temp_storage)
        
        ai_diagnosis = {"root_cause": "test", "confidence": "high", "evidence": [], "osi_layer": "Layer 3", "issue_type": "test", "severity": "high"}
        
        manager.create_review("TEST-001", ai_diagnosis, ReviewDecision.ACCEPTED)
        manager.create_review("TEST-002", ai_diagnosis, ReviewDecision.ACCEPTED)
        manager.create_review("TEST-003", ai_diagnosis, ReviewDecision.EDITED)
        
        accepted = manager.get_accepted_reviews()
        
        assert len(accepted) == 2
        assert all(r.is_accepted() for r in accepted)
    
    def test_update_review(self, temp_storage):
        """Test updating a review."""
        manager = ReviewManager(temp_storage)
        
        ai_diagnosis = {"root_cause": "test", "confidence": "high", "evidence": [], "osi_layer": "Layer 3", "issue_type": "test", "severity": "high"}
        
        manager.create_review("TEST-001", ai_diagnosis, ReviewDecision.ACCEPTED)
        
        updated = manager.update_review(
            case_id="TEST-001",
            reviewer_decision=ReviewDecision.EDITED,
            reviewer_notes="Changed mind"
        )
        
        assert updated is not None
        assert updated.reviewer_decision == ReviewDecision.EDITED
        assert updated.reviewer_notes == "Changed mind"
    
    def test_delete_review(self, temp_storage):
        """Test deleting a review."""
        manager = ReviewManager(temp_storage)
        
        ai_diagnosis = {"root_cause": "test", "confidence": "high", "evidence": [], "osi_layer": "Layer 3", "issue_type": "test", "severity": "high"}
        
        manager.create_review("TEST-001", ai_diagnosis, ReviewDecision.ACCEPTED)
        
        deleted = manager.delete_review("TEST-001")
        
        assert deleted is True
        assert manager.get_review("TEST-001") is None
    
    def test_agreement_calculation(self, temp_storage):
        """Test agreement rate calculation."""
        manager = ReviewManager(temp_storage)
        
        ai_diagnosis = {"root_cause": "test", "confidence": "high", "evidence": [], "osi_layer": "Layer 3", "issue_type": "test", "severity": "high"}
        
        manager.create_review("TEST-001", ai_diagnosis, ReviewDecision.ACCEPTED)
        manager.create_review("TEST-002", ai_diagnosis, ReviewDecision.ACCEPTED)
        manager.create_review("TEST-003", ai_diagnosis, ReviewDecision.EDITED)
        manager.create_review("TEST-004", ai_diagnosis, ReviewDecision.REJECTED)
        
        summary = manager.get_summary()
        
        assert summary.total_reviews == 4
        assert summary.accepted_count == 2
        assert summary.edited_count == 1
        assert summary.rejected_count == 1
        assert summary.agreement_rate == 0.5  # 2/4 accepted


class TestPersistence:
    """Test suite for persistence and reloading."""
    
    @pytest.fixture
    def temp_storage(self):
        """Create a temporary storage file for testing."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        yield temp_path
        # Cleanup
        if Path(temp_path).exists():
            Path(temp_path).unlink()
    
    def test_persistence_save_and_load(self, temp_storage):
        """Test that records persist across manager instances."""
        ai_diagnosis = {"root_cause": "test", "confidence": "high", "evidence": [], "osi_layer": "Layer 3", "issue_type": "test", "severity": "high"}
        
        # Create records with first manager
        manager1 = ReviewManager(temp_storage)
        manager1.create_review("TEST-001", ai_diagnosis, ReviewDecision.ACCEPTED)
        manager1.create_review("TEST-002", ai_diagnosis, ReviewDecision.EDITED)
        
        # Load with second manager
        manager2 = ReviewManager(temp_storage)
        
        assert len(manager2.get_all_reviews()) == 2
        assert manager2.get_review("TEST-001") is not None
        assert manager2.get_review("TEST-002") is not None
    
    def test_export_to_csv(self, temp_storage):
        """Test exporting reviews to CSV."""
        manager = ReviewManager(temp_storage)
        
        ai_diagnosis = {"root_cause": "test", "confidence": "high", "evidence": [], "osi_layer": "Layer 3", "issue_type": "test", "severity": "high"}
        
        manager.create_review("TEST-001", ai_diagnosis, ReviewDecision.ACCEPTED)
        manager.create_review("TEST-002", ai_diagnosis, ReviewDecision.EDITED)
        
        csv_path = temp_storage.replace('.json', '.csv')
        manager.export_to_csv(csv_path)
        
        assert Path(csv_path).exists()
        
        # Cleanup CSV
        if Path(csv_path).exists():
            Path(csv_path).unlink()
    
    def test_corrected_cases_identification(self, temp_storage):
        """Test that corrected cases can be easily identified."""
        manager = ReviewManager(temp_storage)
        
        ai_diagnosis = {"root_cause": "test", "confidence": "high", "evidence": [], "osi_layer": "Layer 3", "issue_type": "test", "severity": "high"}
        
        manager.create_review("TEST-001", ai_diagnosis, ReviewDecision.ACCEPTED)
        manager.create_review("TEST-002", ai_diagnosis, ReviewDecision.EDITED)
        manager.create_review("TEST-003", ai_diagnosis, ReviewDecision.EDITED)
        manager.create_review("TEST-004", ai_diagnosis, ReviewDecision.REJECTED)
        
        summary = manager.get_summary()
        corrected_ids = summary.get_corrected_case_ids()
        
        assert len(corrected_ids) == 2
        assert "TEST-002" in corrected_ids
        assert "TEST-003" in corrected_ids
        assert "TEST-001" not in corrected_ids
