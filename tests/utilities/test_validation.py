import pytest
from datetime import datetime, timedelta

from tests.utilities.test_utility_abstraction import TestIUtility

from dtos.base import EnhancedBaseModel

from utilities.validation import (
    ValidationUtility,
    SecurityValidators,
)


class TestValidationUtility(TestIUtility):
    """Test cases for ValidationUtility class."""

    async def test_validate_password_strength_strong_password(self):
        """Test strong password validation."""
        strong_password = "StrongPass123!"
        result = ValidationUtility.validate_password_strength(strong_password)

        assert result['is_valid'] is True
        assert len(result['issues']) == 0

    async def test_validate_password_strength_weak_password(self):
        """Test weak password validation."""
        weak_password = "weak"
        result = ValidationUtility.validate_password_strength(weak_password)

        assert result['is_valid'] is False
        assert len(result['issues']) > 0
        assert "at least 8 characters" in result['issues'][0]

    async def test_validate_password_strength_common_password(self):
        """Test common password detection."""
        common_password = "password"
        result = ValidationUtility.validate_password_strength(common_password)

        assert result['is_valid'] is False
        assert any("too common" in issue for issue in result['issues'])

    async def test_validate_email_format_valid(self):
        """Test valid email format."""
        valid_email = "test@test.com"
        result = ValidationUtility.validate_email_format(valid_email)

        assert result['is_valid'] is True
        assert result['normalized_email'] == valid_email

    async def test_validate_email_format_invalid(self):
        """Test invalid email format."""
        invalid_email = "invalid-email"
        result = ValidationUtility.validate_email_format(invalid_email)

        assert result['is_valid'] is False
        assert 'error' in result

    async def test_validate_uuid_format_valid(self):
        """Test valid UUID format."""
        valid_uuid = "123e4567-e89b-12d3-a456-426614174000"
        result = ValidationUtility.validate_uuid_format(valid_uuid)

        assert result is True

    async def test_validate_uuid_format_invalid(self):
        """Test invalid UUID format."""
        invalid_uuid = "not-a-uuid"
        result = ValidationUtility.validate_uuid_format(invalid_uuid)

        assert result is False

    async def test_validate_date_range_valid(self):
        """Test valid date range."""
        start_date = datetime.now()
        end_date = start_date + timedelta(days=30)
        result = ValidationUtility.validate_date_range(start_date, end_date)

        assert result['is_valid'] is True

    async def test_validate_date_range_invalid_order(self):
        """Test invalid date range (end before start)."""
        start_date = datetime.now()
        end_date = start_date - timedelta(days=1)
        result = ValidationUtility.validate_date_range(start_date, end_date)

        assert result['is_valid'] is False
        assert 'before end date' in result['error']

    async def test_validate_date_range_too_long(self):
        """Test date range exceeding maximum days."""
        start_date = datetime.now()
        end_date = start_date + timedelta(days=400)
        result = ValidationUtility.validate_date_range(
            start_date,
            end_date,
            max_days=365,
        )

        assert result['is_valid'] is False
        assert 'exceed 365 days' in result['error']

    async def test_sanitize_string_normal(self):
        """Test normal string sanitization."""
        input_string = "Hello, World!"
        result = ValidationUtility.sanitize_string(input_string)

        assert result == "Hello, World!"

    async def test_sanitize_string_with_control_chars(self):
        """Test string sanitization with control characters."""
        input_string = "Hello\x00World\x01!"
        result = ValidationUtility.sanitize_string(input_string)

        assert result == "HelloWorld!"

    async def test_sanitize_string_too_long(self):
        """Test string sanitization with length limit."""
        input_string = "A" * 2000
        result = ValidationUtility.sanitize_string(
            input_string,
            max_length=100,
        )

        assert len(result) == 100
        assert result == "A" * 100

    async def test_validate_numeric_range_valid(self):
        """Test valid numeric range."""
        result = ValidationUtility.validate_numeric_range(5, 1, 10)
        assert result is True

    async def test_validate_numeric_range_invalid(self):
        """Test invalid numeric range."""
        result = ValidationUtility.validate_numeric_range(15, 1, 10)
        assert result is False

    async def test_validate_string_length_valid(self):
        """Test valid string length."""
        result = ValidationUtility.validate_string_length("test", 1, 10)
        assert result is True

    async def test_validate_string_length_invalid(self):
        """Test invalid string length."""
        result = ValidationUtility.validate_string_length("", 1, 10)
        assert result is False


class TestSecurityValidators:
    """Test cases for SecurityValidators class."""

    async def test_validate_sql_injection_prevention_safe(self):
        """Test safe input for SQL injection prevention."""
        safe_input = "Hello, World!"
        result = SecurityValidators.validate_sql_injection_prevention(
            safe_input,
        )

        assert result is True

    async def test_validate_sql_injection_prevention_dangerous(self):
        """Test dangerous input for SQL injection prevention."""
        dangerous_input = "'; DROP TABLE users; --"
        result = SecurityValidators.validate_sql_injection_prevention(
            dangerous_input,
        )

        assert result is False

    async def test_validate_xss_prevention_safe(self):
        """Test safe input for XSS prevention."""
        safe_input = "Hello, World!"
        result = SecurityValidators.validate_xss_prevention(safe_input)

        assert result is True

    async def test_validate_xss_prevention_dangerous(self):
        """Test dangerous input for XSS prevention."""
        dangerous_input = "<script>alert('xss')</script>"
        result = SecurityValidators.validate_xss_prevention(dangerous_input)

        assert result is False

    async def test_validate_path_traversal_prevention_safe(self):
        """Test safe input for path traversal prevention."""
        safe_input = "normal/path/file.txt"
        result = SecurityValidators.validate_path_traversal_prevention(
            safe_input,
        )

        assert result is True

    async def test_validate_path_traversal_prevention_dangerous(self):
        """Test dangerous input for path traversal prevention."""
        dangerous_input = "../../../etc/passwd"
        result = SecurityValidators.validate_path_traversal_prevention(
            dangerous_input,
        )

        assert result is False


class TestEnhancedBaseModel:
    """Test cases for EnhancedBaseModel class."""

    async def test_sanitize_strings_validator(self):
        """Test string sanitization validator."""
        class TestModel(EnhancedBaseModel):
            name: str
            description: str

        model = TestModel(name="John Doe", description="A test description")
        assert model.name == "John Doe"
        assert model.description == "A test description"

    async def test_validate_security_safe(self):
        """Test security validation with safe input."""
        class TestModel(EnhancedBaseModel):
            name: str
            email: str

        model = TestModel(name="John Doe", email="john@example.com")
        result = model.validate_security()

        assert result['is_valid'] is True
        assert len(result['issues']) == 0

    async def test_validate_security_dangerous(self):
        """Test security validation with dangerous input."""
        class TestModel(EnhancedBaseModel):
            name: str
            comment: str

        model = TestModel(
            name="John Doe",
            comment="<script>alert('xss')</script>"
        )
        result = model.validate_security()

        assert result['is_valid'] is False
        assert len(result['issues']) > 0
        assert any("XSS" in issue for issue in result['issues'])

    async def test_extra_fields_forbidden(self):
        """Test that extra fields are forbidden."""
        class TestModel(EnhancedBaseModel):
            name: str

        with pytest.raises(ValueError):
            TestModel(name="John", age=30)
