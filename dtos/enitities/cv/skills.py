from pydantic import BaseModel, Field
from typing import List


class Skills(BaseModel):
    """Skills grouping."""
    technical: List[str] = Field(default_factory=list)
    soft: List[str] = Field(default_factory=list)
    tools: List[str] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)
