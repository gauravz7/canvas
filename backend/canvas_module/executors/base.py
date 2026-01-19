from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from services.log_service import log_service
import logging

logger = logging.getLogger(__name__)

class BaseNodeExecutor(ABC):
    """Abstract base class for all node executors."""
    
    def __init__(self, services: Dict[str, Any]):
        """
        Initialize with necessary services.
        services dict should contain: 'gemini', 'veo', 'vertex', 'storage', 'config'
        """
        self.services = services
        self.logger = logger

    @abstractmethod
    async def execute(self, node: Any, inputs: Dict[str, Any], user_id: str, context: Dict[str, Any] = None) -> Any:
        """
        Execute the node logic.
        
        Args:
            node: The Node object containing data and configuration.
            inputs: Dictionary of resolved inputs.
            user_id: The ID of the user triggering execution.
            context: Global execution context (optional).
            
        Returns:
            The output of the node execution.
        """
        pass

    def _get_config(self, node: Any, key: str, default: Any = None) -> Any:
        """Helper to safely get config values."""
        return node.data.config.get(key, default) if node.data.config else default
