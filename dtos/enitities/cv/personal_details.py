from pydantic import BaseModel


class PersonalDetails(BaseModel):
    """Candidate personal information."""
    name: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    linkedin: str = ""
