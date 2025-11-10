"""
API Logical Keys (APILK) constants for identifying API operations.
"""
from typing import Final


class APILK:
    """
    Logical keys for API operations, used for routing and identification.
    """
    
    # Ranking Job APIs
    CREATE_RANKING_JOB: Final[str] = "CREATE_RANKING_JOB"
    FETCH_RANKING_JOB_STATUS: Final[str] = "FETCH_RANKING_JOB_STATUS"
    FETCH_RANKING_JOB_RESULT: Final[str] = "FETCH_RANKING_JOB_RESULT"