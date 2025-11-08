"""
Base response DTO for API responses, providing standard response fields.
"""
from pydantic import BaseModel
from typing import List, Dict, Union, Optional


class BaseResponseDTO(BaseModel):
    """
    Base DTO for API responses.
    Fields:
        transactionUrn (str): Unique transaction identifier.
        status (str): Status of the response (e.g., 'success', 'error').
        responseMessage (str): Human-readable message for the response.
        responseKey (str): Key for programmatic response handling.
        data (List | Dict, optional): Main response data payload.
        errors (List | Dict, optional): Error details if any.
    """
    transactionUrn: str
    status: str
    responseMessage: str
    responseKey: str
    data: Optional[Union[List, Dict]] = None
    errors: Optional[Union[List, Dict]] = None
