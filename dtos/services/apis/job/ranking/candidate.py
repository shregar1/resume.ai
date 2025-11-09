from pydantic import BaseModel, Field
from typing import List


class CandidateResult(BaseModel):
    """Candidate ranking result."""
    rank: int
    candidate_name: str
    tier: str
    total_score: float
    skills_score: float
    experience_score: float
    education_score: float
    strengths: List[str]
    weaknesses: List[str]
    explanation: str