from pydantic import BaseModel, Field
from typing import List

from dtos.enitities.match.skill import SkillMatch


class Matches(BaseModel):
    """Matching details."""
    matched_skills: List[SkillMatch] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    extra_skills: List[str] = Field(default_factory=list)
