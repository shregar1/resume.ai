"""
APIStatus constants for representing API response status.
"""
from typing import Final


class APIStatus:
    """
    Status values for API responses.
    """
    SUCCESS: Final[str] = "SUCCESS"
    FAILED: Final[str] = "FAILED"
    PENDING: Final[str] = "PENDING"
