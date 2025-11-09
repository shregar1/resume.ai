"""
Regular expressions and patterns for input validation and security checks.
"""
import re

from typing import Final, List


class RegularExpression:
    """
    Collection of regular expressions for validating and securing input data.
    Includes patterns for dates, passwords, emails, phone numbers,
    SQL injection, XSS, and path traversal.
    """
    DD_MM_YYYY: Final[str] = r"\b\d{2}/\d{2}/\d{4}\b"
    PASSWORD_PATTERN: Final[re.Pattern] = re.compile(
        r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
    )
    EMAIL_PATTERN: Final[re.Pattern] = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    PHONE_PATTERN: Final[re.Pattern] = re.compile(
        r'^\+?1?\d{9,15}$'
    )
    ALPHANUMERIC_PATTERN: Final[re.Pattern] = re.compile(
        r'^[a-zA-Z0-9\s\-_]+$'
    )
    DANGEROUS_SQL_INJECTION_PATTERNS: Final[List[str]] = [
            r'(\b(union|select|insert|update|delete|drop|create|alter|exec|\
                execute)\b)',
            r'(\b(or|and)\b\s+\d+\s*=\s*\d+)',
            r'(\b(union|select|insert|update|delete|drop|create|alter|exec|\
                execute)\b.*\b(union|select|insert|update|delete|drop|create|\
                alter|exec|execute)\b)',
            r'(\b(union|select|insert|update|delete|drop|create|alter|exec|\
                execute)\b.*\b(union|select|insert|update|delete|drop|create|\
                alter|exec|execute)\b.*\b(union|select|insert|update|delete|\
                drop|create|alter|exec|execute)\b)',
        ]

    DANGEROUS_XSS_PATTERNS: Final[List[str]] = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'on\w+\s*=',
            r'<iframe[^>]*>',
            r'<object[^>]*>',
            r'<embed[^>]*>',
        ]

    DANGEROUS_PATH_TRAVERSAL_PATTERNS: Final[List[str]] = [
            r'\.\./',
            r'\.\.\\',
            r'%2e%2e%2f',
            r'%2e%2e%5c',
        ]
