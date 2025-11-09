"""Base agent class for the multi-agent system."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging
from datetime import datetime
import uuid

from src.models.schemas import AgentMessage


class BaseAgent(ABC):
    """Base class for all agents in the system."""
    
    def __init__(self, agent_name: str):
        """Initialize the agent.
        
        Args:
            agent_name: Name of the agent
        """
        self.agent_name = agent_name
        self.logger = logging.getLogger(f"agent.{agent_name}")
        self.logger.info(f"Initializing {agent_name}")
    
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

