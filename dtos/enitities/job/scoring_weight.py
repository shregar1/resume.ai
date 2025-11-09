from pydantic import BaseModel

from constants.scoring_weight import ScoringWeightConstant


class ScoringWeights(BaseModel):
    """Scoring weights."""

    skills: float = ScoringWeightConstant.SKILLS
    experience: float = ScoringWeightConstant.EXPERIENCE
    education: float = ScoringWeightConstant.EDUCATION
    career_trajectory: float = ScoringWeightConstant.CAREER_TRAJECTORY
    other: float = ScoringWeightConstant.OTHER