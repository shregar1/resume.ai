from typing import Final

class WorkflowStatusConstant:
    """Workflow statuses."""
    INITIALIZED: Final[str] = "initialized"
    PARSING: Final[str] = "parsing"
    ANALYZING_JD: Final[str] = "analyzing_jd"
    MATCHING: Final[str] = "matching"
    SCORING: Final[str] = "scoring"
    RANKING: Final[str] = "ranking"
    GENERATING_REPORT: Final[str] = "generating_report"
    COMPLETED: Final[str] = "completed"
    FAILED: Final[str] = "failed"
