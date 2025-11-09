from pydantic import BaseModel
from typing import Optional


class Certification(BaseModel):
    """Certification entry."""
    name: str
    issuer: str
    date: Optional[str] = None
