"""
DTO for USDA API configuration settings.
"""
from pydantic import BaseModel


class USDAConfigurationDTO(BaseModel):
    """
    DTO for USDA API configuration.
    Fields:
        url (str): USDA API base URL.
    """
    url: str
