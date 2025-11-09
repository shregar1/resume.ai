from pydantic import BaseModel
from typing import Optional


class Education(BaseModel):
    """Education entry."""
    institution: str
    degree: str
    field: str
    graduation_year: Optional[int] = None
    gpa: Optional[float] = None

