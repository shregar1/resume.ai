from pydantic import BaseModel
from typing import List
from dtos.services.apis.job.ranking.candidate import CandidateResult


class RankingResults(BaseModel):
    """Complete ranking results."""
    job_id: str
    job_title: str
    total_candidates: int
    tier_distribution: dict
    top_candidates: List[CandidateResult]
    completed_at: str