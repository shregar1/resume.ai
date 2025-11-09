from pydantic import BaseModel, Field
from typing import List

from dtos.enitities.job.seniority_level import SeniorityLevel
from dtos.enitities.job.requirements import JobRequirements
from dtos.enitities.job.scoring_weight import ScoringWeights


class JobDescription(BaseModel):
    """Job description model."""

    jd_id: str
    job_title: str
    company: str = ""
    department: str = ""
    seniority_level: SeniorityLevel = SeniorityLevel.MID
    requirements: JobRequirements = Field(default_factory=JobRequirements)
    responsibilities: List[str] = Field(default_factory=list)
    scoring_weights: ScoringWeights = Field(default_factory=ScoringWeights)
    full_description: str = ""