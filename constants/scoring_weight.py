from typing import Final


class ScoringWeightConstant:
    """Constants for scoring."""

    SKILLS: Final[float] = 0.4
    EXPERIENCE: Final[float] = 0.3
    EDUCATION: Final[float] = 0.15
    CAREER_TRAJECTORY: Final[float] = 0.1
    OTHER: Final[float] = 0.05