import uuid
from pydantic import BaseModel, field_validator


class IRequestDTO(BaseModel):

    reference_number: str

    @field_validator('reference_number')
    @classmethod
    def validate_reference_number(cls, v):
        if not v or not v.strip():
            raise ValueError('Reference number cannot be empty.')
        try:
            uuid.UUID(v)
        except Exception:
            raise ValueError('Reference number must be a valid UUID.')
        return v
