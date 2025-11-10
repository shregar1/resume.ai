from pydantic import BaseModel, field_validator
from typing import Optional, List


class CreateRankingJobRequestDTO(BaseModel):
    """Request model for ranking job."""
    job_description: str
    job_title: Optional[str] = ""
    company: Optional[str] = ""
    cv_files: List[str] = []

    @field_validator("job_description")
    def validate_job_description(value: str) -> str:
        """Validate the job description."""
        if not value:
            raise ValueError("Job description is required")
        return value

    @field_validator("job_title")
    def validate_job_title(value: str) -> str:
        """Validate the job title."""
        if not value:
            raise ValueError("Job title is required")
        return value
        
    @field_validator("company")
    def validate_company(value: str) -> str:
        """Validate the company."""
        if not value:
            raise ValueError("Company is required")
        return value

    @field_validator("cv_files")
    def validate_cv_files(value: List[str]) -> List[str]:
        """Validate the CV files."""
        if not value:
            raise ValueError("CV files are required")
        return value







