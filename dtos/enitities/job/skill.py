from pydantic import BaseModel


class Skill(BaseModel):
    """Skill with weight."""
    skill: str
    weight: float = 1.0

