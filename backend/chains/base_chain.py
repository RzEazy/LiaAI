from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseChain(ABC):
    """Base class for all processing chains"""
    
    @abstractmethod
    def process(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process the user input and return a response
        
        Args:
            user_input: The user's input text
            context: Additional context (memory, previous interactions, etc.)
            
        Returns:
            Dictionary containing:
                - response: The main response text
                - metadata: Additional information about the processing
        """
        pass