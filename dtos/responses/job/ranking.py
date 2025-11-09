from pydantic import BaseModel


class RankingResponse(BaseModel):
    """Response model for ranking job."""
    job_id: str
    status: str
    message: str
