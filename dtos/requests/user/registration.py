"""
DTO for user registration request payload, with validation for email and
password fields.
"""
from pydantic import EmailStr, field_validator

from dtos.requests.abstraction import IRequestDTO

from dtos.base import EnhancedBaseModel

from utilities.validation import ValidationUtility


class UserRegistrationRequestDTO(IRequestDTO, EnhancedBaseModel):
    """
    DTO for user registration request.
    Fields:
        email (EmailStr): User's email address (validated).
        password (str): User's password (validated for length and non-empty).
    """
    email: EmailStr
    password: str

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if not v or not v.strip():
            raise ValueError('Password cannot be empty.')

        validation_result = ValidationUtility.validate_password_strength(v)
        if not validation_result['is_valid']:
            issues = ', '.join(validation_result['issues'])
            message = f"Password validation failed: {issues}"
            raise ValueError(message)

        return v

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        validation_result = ValidationUtility.validate_email_format(v)
        if not validation_result['is_valid']:
            raise ValueError(
                f"Invalid email format: {validation_result['error']}"
            )
        return validation_result['normalized_email']
