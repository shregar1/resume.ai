from pydantic import BaseModel, Field
from typing import List, Optional


class RankingRequest(BaseModel):
    """Request model for ranking job."""
    job_description: str
    job_title: Optional[str] = ""
    company: Optional[str] = ""








