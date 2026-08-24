"""Review manager for human review workflow."""

import json
import csv
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from review.schemas import ReviewRecord, ReviewDecision, ReviewSummary

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReviewManager:
    """Manages human review records for AI diagnoses."""
    
    def __init__(self, storage_path: str = "data/reviews.json"):
        """
        Initialize the review manager.
        
        Args:
            storage_path: Path to the storage file for review records
        """
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._records: List[ReviewRecord] = []
        self._load_records()
    
    def _load_records(self) -> None:
        """Load review records from storage."""
        if not self.storage_path.exists():
            logger.info(f"Creating new review storage at {self.storage_path}")
            self._records = []
            return
        
        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self._records = [ReviewRecord(**record) for record in data]
            logger.info(f"Loaded {len(self._records)} review records from {self.storage_path}")
        except Exception as e:
            logger.error(f"Error loading review records: {e}")
            self._records = []
    
    def _save_records(self) -> None:
        """Save review records to storage."""
        try:
            data = [record.model_dump() for record in self._records]
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
            logger.info(f"Saved {len(self._records)} review records to {self.storage_path}")
        except Exception as e:
            logger.error(f"Error saving review records: {e}")
            raise
    
    def create_review(
        self,
        case_id: str,
        ai_diagnosis: Dict[str, Any],
        reviewer_decision: ReviewDecision,
        corrected_diagnosis: Optional[Dict[str, Any]] = None,
        reviewer_notes: Optional[str] = None,
        reason_for_correction: Optional[str] = None
    ) -> ReviewRecord:
        """
        Create a new review record.
        
        Args:
            case_id: ID of the case being reviewed
            ai_diagnosis: Original AI diagnosis response
            reviewer_decision: Reviewer's decision (ACCEPTED/EDITED/REJECTED)
            corrected_diagnosis: Corrected diagnosis if edited
            reviewer_notes: Reviewer's notes
            reason_for_correction: Reason for correction/rejection
            
        Returns:
            Created ReviewRecord
        """
        # Determine final diagnosis and agreement
        if reviewer_decision == ReviewDecision.ACCEPTED:
            final_diagnosis = ai_diagnosis
            ai_human_agreed = True
        elif reviewer_decision == ReviewDecision.EDITED:
            final_diagnosis = corrected_diagnosis or ai_diagnosis
            ai_human_agreed = False
        else:  # REJECTED
            final_diagnosis = ai_diagnosis  # Keep AI diagnosis for reference
            ai_human_agreed = False
        
        record = ReviewRecord(
            case_id=case_id,
            ai_diagnosis=ai_diagnosis,
            reviewer_decision=reviewer_decision,
            corrected_diagnosis=corrected_diagnosis,
            reviewer_notes=reviewer_notes,
            reason_for_correction=reason_for_correction,
            final_diagnosis=final_diagnosis,
            ai_human_agreed=ai_human_agreed
        )
        
        self._records.append(record)
        self._save_records()
        
        logger.info(f"Created review for case {case_id}: {reviewer_decision}")
        return record
    
    def get_review(self, case_id: str) -> Optional[ReviewRecord]:
        """
        Get review record for a specific case.
        
        Args:
            case_id: ID of the case
            
        Returns:
            ReviewRecord if found, None otherwise
        """
        for record in self._records:
            if record.case_id == case_id:
                return record
        return None
    
    def get_all_reviews(self) -> List[ReviewRecord]:
        """
        Get all review records.
        
        Returns:
            List of all ReviewRecord objects
        """
        return self._records.copy()
    
    def get_corrected_reviews(self) -> List[ReviewRecord]:
        """
        Get all reviews that resulted in corrections.
        
        Returns:
            List of corrected ReviewRecord objects
        """
        return [r for r in self._records if r.is_corrected()]
    
    def get_rejected_reviews(self) -> List[ReviewRecord]:
        """
        Get all reviews that resulted in rejection.
        
        Returns:
            List of rejected ReviewRecord objects
        """
        return [r for r in self._records if r.is_rejected()]
    
    def get_accepted_reviews(self) -> List[ReviewRecord]:
        """
        Get all reviews that were accepted without changes.
        
        Returns:
            List of accepted ReviewRecord objects
        """
        return [r for r in self._records if r.is_accepted()]
    
    def update_review(
        self,
        case_id: str,
        reviewer_decision: Optional[ReviewDecision] = None,
        corrected_diagnosis: Optional[Dict[str, Any]] = None,
        reviewer_notes: Optional[str] = None,
        reason_for_correction: Optional[str] = None
    ) -> Optional[ReviewRecord]:
        """
        Update an existing review record.
        
        Args:
            case_id: ID of the case to update
            reviewer_decision: New reviewer decision
            corrected_diagnosis: New corrected diagnosis
            reviewer_notes: New reviewer notes
            reason_for_correction: New reason for correction
            
        Returns:
            Updated ReviewRecord if found, None otherwise
        """
        record = self.get_review(case_id)
        if not record:
            logger.warning(f"No review found for case {case_id}")
            return None
        
        # Update fields if provided
        if reviewer_decision is not None:
            record.reviewer_decision = reviewer_decision
        
        if corrected_diagnosis is not None:
            record.corrected_diagnosis = corrected_diagnosis
        
        if reviewer_notes is not None:
            record.reviewer_notes = reviewer_notes
        
        if reason_for_correction is not None:
            record.reason_for_correction = reason_for_correction
        
        # Recalculate final diagnosis and agreement
        if record.reviewer_decision == ReviewDecision.ACCEPTED:
            record.final_diagnosis = record.ai_diagnosis
            record.ai_human_agreed = True
        elif record.reviewer_decision == ReviewDecision.EDITED:
            record.final_diagnosis = record.corrected_diagnosis or record.ai_diagnosis
            record.ai_human_agreed = False
        else:  # REJECTED
            record.final_diagnosis = record.ai_diagnosis
            record.ai_human_agreed = False
        
        self._save_records()
        logger.info(f"Updated review for case {case_id}")
        return record
    
    def delete_review(self, case_id: str) -> bool:
        """
        Delete a review record.
        
        Args:
            case_id: ID of the case to delete
            
        Returns:
            True if deleted, False if not found
        """
        for i, record in enumerate(self._records):
            if record.case_id == case_id:
                del self._records[i]
                self._save_records()
                logger.info(f"Deleted review for case {case_id}")
                return True
        logger.warning(f"No review found for case {case_id}")
        return False
    
    def get_summary(self) -> ReviewSummary:
        """
        Get summary statistics for all reviews.
        
        Returns:
            ReviewSummary with statistics
        """
        total = len(self._records)
        accepted = len(self.get_accepted_reviews())
        edited = len(self.get_corrected_reviews())
        rejected = len(self.get_rejected_reviews())
        
        agreement_rate = accepted / total if total > 0 else 0.0
        
        corrected_case_ids = [r.case_id for r in self.get_corrected_reviews()]
        
        return ReviewSummary(
            total_reviews=total,
            accepted_count=accepted,
            edited_count=edited,
            rejected_count=rejected,
            agreement_rate=agreement_rate,
            corrected_cases=corrected_case_ids
        )
    
    def export_to_csv(self, output_path: str = "data/reviews_export.csv") -> None:
        """
        Export review records to CSV format.
        
        Args:
            output_path: Path to the output CSV file
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        if not self._records:
            logger.warning("No records to export")
            return
        
        fieldnames = [
            'case_id',
            'timestamp',
            'reviewer_decision',
            'ai_human_agreed',
            'reviewer_notes',
            'reason_for_correction',
            'ai_diagnosis',
            'corrected_diagnosis',
            'final_diagnosis'
        ]
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for record in self._records:
                writer.writerow({
                    'case_id': record.case_id,
                    'timestamp': record.timestamp.isoformat(),
                    'reviewer_decision': record.reviewer_decision.value,
                    'ai_human_agreed': record.ai_human_agreed,
                    'reviewer_notes': record.reviewer_notes,
                    'reason_for_correction': record.reason_for_correction,
                    'ai_diagnosis': json.dumps(record.ai_diagnosis),
                    'corrected_diagnosis': json.dumps(record.corrected_diagnosis) if record.corrected_diagnosis else '',
                    'final_diagnosis': json.dumps(record.final_diagnosis)
                })
        
        logger.info(f"Exported {len(self._records)} reviews to {output_file}")


def get_review_manager(storage_path: str = "data/reviews.json") -> ReviewManager:
    """
    Convenience function to get a ReviewManager instance.
    
    Args:
        storage_path: Path to the storage file
        
    Returns:
        ReviewManager instance
    """
    return ReviewManager(storage_path)
