"""Base agent class for the multi-agent system."""
import uuid

from abc import abstractmethod
from datetime import datetime
from typing import Dict, Any, Optional

from abstractions.agent import IAgent

from dtos.services.agents.message import AgentMessage


class BaseAgent(IAgent):
    """Base class for all agents in the system."""
    
    def __init__(self,
        urn: str = None,
        user_urn: str = None,
        api_name: str = None,
        user_id: str = None,
    ):
        super().__init__(
            urn=urn,
            user_urn=user_urn,
            api_name=api_name,
            user_id=user_id,
        )
        self.logger.info("Initializing base agent")
    
    @abstractmethod
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process data and return results.
        
        Args:
            data: Input data to process
            
        Returns:
            Processing results
        """
        pass
    
    def create_message(
        self,
        target_agent: str,
        message_type: str,
        payload: Dict[str, Any],
        correlation_id: Optional[str] = None,
        priority: str = "medium"
    ) -> AgentMessage:
        """Create a standard agent message.
        
        Args:
            target_agent: Target agent name
            message_type: Type of message (task, result, error, status)
            payload: Message payload
            correlation_id: Correlation ID for tracking
            priority: Message priority
            
        Returns:
            Formatted agent message
        """
        return AgentMessage(
            message_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            source_agent=self.agent_name,
            target_agent=target_agent,
            message_type=message_type,
            priority=priority,
            payload=payload,
            correlation_id=correlation_id or str(uuid.uuid4()),
            retry_count=0
        )
    
    async def handle_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle errors during processing.
        
        Args:
            error: The exception that occurred
            context: Context information
            
        Returns:
            Error response
        """
        self.logger.error(f"Error in {self.agent_name}: {str(error)}", exc_info=True)
        return {
            "success": False,
            "error": str(error),
            "agent": self.agent_name,
            "context": context
        }
    
    def log_metrics(self, metrics: Dict[str, Any]):
        """Log agent metrics.
        
        Args:
            metrics: Metrics to log
        """
        self.logger.info(f"Metrics for {self.agent_name}: {metrics}")
