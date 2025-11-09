"""
Constants for request and response payload types.
"""
from typing import Final


class RequestPayloadType:
    """
    Supported request payload types for API endpoints.
    """
    JSON: Final[str] = "json"
    FORM: Final[str] = "form"
    FILES: Final[str] = "files"
    QUERY: Final[str] = "query"


class ResponsePlayloadType:
    """
    Supported response payload types for API endpoints.
    """
    JSON: Final[str] = "json"
    TEXT: Final[str] = "text"
    CONTENT: Final[str] = "content"
