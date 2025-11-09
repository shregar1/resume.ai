from pydantic import BaseModel

from constants.candidate_tier import CandidateTierConstant


class CandidateTier(BaseModel):
    """Candidate tiers."""

    A: str = CandidateTierConstant.A
    B: str = CandidateTierConstant.B
    C: str = CandidateTierConstant.C
    D: str = CandidateTierConstant.D