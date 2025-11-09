from pydantic import BaseModel, Field
from typing import List

from dtos.enitities.candidate.tier import CandidateTier
from dtos.enitities.match.score import Scores
from dtos.enitities.match.data import Matches


class CandidateScore(BaseModel):
    """Candidate scoring result."""

    candidate_id: str
    cv_id: str
    jd_id: str
    candidate_name: str = ""
    scores: Scores = Field(default_factory=Scores)
    matches: Matches = Field(default_factory=Matches)
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    explanation: str = ""
    rank: int = 0
    tier: CandidateTier = CandidateTier.C


