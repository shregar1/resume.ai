from pydantic import BaseModel


class Scores(BaseModel):
    """Score breakdown."""
    total: float = 0.0
    skills_match: float = 0.0
    experience_relevance: float = 0.0
    education_fit: float = 0.0
    career_trajectory: float = 0.0
    confidence: float = 0.0