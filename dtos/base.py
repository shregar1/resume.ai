from datetime import datetime
from pydantic import BaseModel, validator
from typing import Any, Dict

from utilities.validation import ValidationUtility, SecurityValidators

from start_utils import logger


class EnhancedBaseModel(BaseModel):
    """
    Enhanced base model with additional validation capabilities.
    """

    class Config:
        extra = "forbid"  # Reject extra fields
        validate_assignment = True  # Validate on assignment
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }

    @validator('*', pre=True)
    def sanitize_strings(cls, v):
        """Sanitize all string inputs."""
        logger.debug("Sanitizing all string inputs in EnhancedBaseModel")
        if isinstance(v, str):
            return ValidationUtility.sanitize_string(v)
        return v

    def validate_security(self) -> Dict[str, Any]:
        """Perform security validation on all string fields."""
        logger.debug("Performing security validation on EnhancedBaseModel")
        issues = []

        for field_name, field_value in self.dict().items():
            if isinstance(field_value, str):
                if not SecurityValidators.validate_sql_injection_prevention(
                    field_value,
                ):
                    issues.append(
                        f"Potential SQL injection in field '{field_name}'"
                    )

                if not SecurityValidators.validate_xss_prevention(field_value):
                    issues.append(f"Potential XSS in field '{field_name}'")

                if not SecurityValidators.validate_path_traversal_prevention(
                    field_value,
                ):
                    issues.append(
                        f"Potential path traversal in field '{field_name}'"
                    )

        return {
            'is_valid': len(issues) == 0,
            'issues': issues
        }
