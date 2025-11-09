from pydantic import BaseModel


class SkillMatch(BaseModel):
    """Individual skill match."""
    skill: str
    cv_proficiency: str = "unknown"
    jd_requirement: str = "required"
    match_score: float = 0.0
