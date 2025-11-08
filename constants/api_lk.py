"""
API Logical Keys (APILK) constants for identifying API operations.
"""
from typing import Final


class APILK:
    """
    Logical keys for API operations, used for routing and identification.
    """
    LOGIN: Final[str] = "LOGIN"
    REGISTRATION: Final[str] = "REGISTRATION"
    LOGOUT: Final[str] = "LOGOUT"
