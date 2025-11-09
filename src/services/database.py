"""Database service for storing CV ranking data."""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
import json

# This is a simple in-memory implementation
# In production, use SQLAlchemy with PostgreSQL

logger = logging.getLogger(__name__)


class DatabaseService:
    """Service for database operations."""
    
    def __init__(self):
        """Initialize database service."""
        self.jobs = {}
        self.candidates = {}
        logger.info("Database service initialized (in-memory mode)")
    
    async def create_job(
        self,
        job_id: str,
        job_data: Dict[str, Any]
    ) -> bool:
        """Create a new ranking job.
        
        Args:
            job_id: Job ID
            job_data: Job data
            
        Returns:
            Success status
        """
        try:
            self.jobs[job_id] = {
                **job_data,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            return True
        except Exception as e:
            logger.error(f"Error creating job: {e}")
            return False
    
    async def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get a ranking job by ID.
        
        Args:
            job_id: Job ID
            
        Returns:
            Job data or None
        """
        return self.jobs.get(job_id)
    
    async def update_job(
        self,
        job_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """Update a ranking job.
        
        Args:
            job_id: Job ID
            updates: Updates to apply
            
        Returns:
            Success status
        """
        try:
            if job_id in self.jobs:
                self.jobs[job_id].update(updates)
                self.jobs[job_id]["updated_at"] = datetime.now().isoformat()
                return True
            return False
        except Exception as e:
            logger.error(f"Error updating job: {e}")
            return False
    
    async def delete_job(self, job_id: str) -> bool:
        """Delete a ranking job.
        
        Args:
            job_id: Job ID
            
        Returns:
            Success status
        """
        try:
            if job_id in self.jobs:
                del self.jobs[job_id]
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting job: {e}")
            return False
    
    async def list_jobs(
        self,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List ranking jobs.
        
        Args:
            limit: Maximum number of jobs to return
            offset: Offset for pagination
            
        Returns:
            List of jobs
        """
        jobs_list = list(self.jobs.values())
        return jobs_list[offset:offset + limit]
    
    async def save_candidate_score(
        self,
        candidate_data: Dict[str, Any]
    ) -> bool:
        """Save candidate score.
        
        Args:
            candidate_data: Candidate data
            
        Returns:
            Success status
        """
        try:
            candidate_id = candidate_data.get("candidate_id")
            self.candidates[candidate_id] = candidate_data
            return True
        except Exception as e:
            logger.error(f"Error saving candidate: {e}")
            return False
    
    async def get_candidates_by_job(
        self,
        job_id: str
    ) -> List[Dict[str, Any]]:
        """Get all candidates for a job.
        
        Args:
            job_id: Job ID
            
        Returns:
            List of candidates
        """
        return [
            c for c in self.candidates.values()
            if c.get("jd_id") == job_id
        ]


# Global database instance
db_service = DatabaseService()

