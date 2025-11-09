from pydantic import BaseModel
from constants.workflow_satus import WorkflowStatusConstant


class WorkflowStatus(BaseModel):
    """Workflow statuses."""

    INITIALIZED: str = WorkflowStatusConstant.INITIALIZED
    PARSING: str = WorkflowStatusConstant.PARSING
    ANALYZING_JD: str = WorkflowStatusConstant.ANALYZING_JD
    MATCHING: str = WorkflowStatusConstant.MATCHING
    SCORING: str = WorkflowStatusConstant.SCORING
    RANKING: str = WorkflowStatusConstant.RANKING
    GENERATING_REPORT: str = WorkflowStatusConstant.GENERATING_REPORT
    COMPLETED: str = WorkflowStatusConstant.COMPLETED
    FAILED: str = WorkflowStatusConstant.FAILED
