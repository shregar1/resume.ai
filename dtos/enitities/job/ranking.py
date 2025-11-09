from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from dtos.enitities.candidate.score import CandidateScore
from dtos.enitities.workflow.status import WorkflowStatus


class RankingJob(BaseModel):
    """Ranking job tracking."""

    job_id: str
    status: WorkflowStatus = WorkflowStatus.INITIALIZED
    cv_count: int = 0
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    jd_id: Optional[str] = None
    results: List[CandidateScore] = Field(default_factory=list)
    error_message: Optional[str] = None

