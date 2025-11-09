from pydantic import BaseModel, Field
from typing import List

from dtos.enitities.job.skill import Skill


class JobRequirements(BaseModel):
    """Job requirements."""

    must_have_skills: List[Skill] = Field(default_factory=list)
    nice_to_have_skills: List[Skill] = Field(default_factory=list)
    min_experience_years: float = 0.0
    education_level: str = ""
    industry_experience: List[str] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
