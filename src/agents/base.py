from abc import ABC, abstractmethod
from typing import Any

class BaseAgent(ABC):
    """Abstract base for all agents."""
    
    @abstractmethod
    def execute(self, input_data: Any) -> Any:
        pass