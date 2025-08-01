import dataclasses
from typing import Any, Dict, Optional

@dataclasses.dataclass
class Message:
    sender: str
    receiver: str
    content: Any
    message_type: str
    timestamp: Optional[str] = None # Consider adding a timestamp for logging/ordering

@dataclasses.dataclass
class Context:
    # This will hold shared state, input data, and analysis results
    # It can be extended as needed based on the specific interactions
    input_data: Optional[Dict[str, Any]] = None
    shared_analysis_results: Optional[Dict[str, Any]] = None
    # Add other context variables as they become apparent during agent interaction design
    # For example:
    # current_task_id: Optional[str] = None
    # conversation_history: Optional[List[Message]] = None
