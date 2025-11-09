from pydantic import BaseModel

from constants.seniority_level import SeniorityLevelConstant


class SeniorityLevel(BaseModel):
    """Seniority levels."""

    ENTRY = SeniorityLevelConstant.ENTRY
    MID = SeniorityLevelConstant.MID
    SENIOR = SeniorityLevelConstant.SENIOR
    PRINCIPAL = SeniorityLevelConstant.PRINCIPAL
    DIRECTOR = SeniorityLevelConstant.DIRECTOR
    VP = SeniorityLevelConstant.VP
    CTO = SeniorityLevelConstant.CTO
    CEO = SeniorityLevelConstant.CEO