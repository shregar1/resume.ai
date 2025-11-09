from pydantic import BaseModel, Field
from typing import Optional, List


class WorkExperience(BaseModel):
    """Work experience entry."""
    company: str
    role: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    duration_months: Optional[int] = None
    description: str = ""
    key_achievements: List[str] = Field(default_factory=list)
    technologies: List[str] = Field(default_factory=list)
