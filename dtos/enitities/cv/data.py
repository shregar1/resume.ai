from pydantic import BaseModel, Field
from typing import List, Dict, Any

from dtos.enitities.cv.personal_details import PersonalDetails
from dtos.enitities.cv.work_experience import WorkExperience
from dtos.enitities.cv.education import Education
from dtos.enitities.cv.skills import Skills
from dtos.enitities.cv.certification import Certification
from dtos.enitities.cv.project import Project


class CVData(BaseModel):
    """Structured CV data."""
    cv_id: str
    candidate: PersonalDetails
    summary: str = ""
    experience: List[WorkExperience] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)
    skills: Skills = Field(default_factory=Skills)
    certifications: List[Certification] = Field(default_factory=list)
    projects: List[Project] = Field(default_factory=list)
    total_experience_years: float = 0.0
    metadata: Dict[str, Any] = Field(default_factory=dict)

