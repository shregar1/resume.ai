from datetime import datetime
from typing import Dict, Any
from pydantic import BaseModel, Field


class AgentMessage(BaseModel):
    """Standard agent message format."""
    message_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    source_agent: str
    target_agent: str
    message_type: str  # task, result, error, status
    priority: str = "medium"  # high, medium, low
    payload: Dict[str, Any] = Field(default_factory=dict)
    correlation_id: str
    retry_count: int = 0