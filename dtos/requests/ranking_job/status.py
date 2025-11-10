from pydantic import BaseModel
from pydantic import field_validator


class FetchRankingJobStatusRequestDTO(BaseModel):
    """Request model for fetching the status of a ranking job."""
    job_id: str

    @field_validator("job_id")
    def validate_job_id(value: str) -> str:
        """Validate the job ID."""
        if not value:
            raise ValueError("Job ID is required")
        return value