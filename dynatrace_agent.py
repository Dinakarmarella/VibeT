import sys
import os

# Add the directory containing slm_automation.py to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from slm_automation import query_dynatrace_logs
from MCP.mcp_core import Message, Context

class DynatraceAgent:
    def __init__(self):
        pass

    def process_message(self, input_message: Message, context: Context) -> Message:
        if input_message.message_type == "query_dynatrace_logs_request":
            query = input_message.content.get("query")
            time_frame = input_message.content.get("time_frame", "-1h")
            if query:
                logs_response = query_dynatrace_logs(query, time_frame)
                if "error" not in logs_response:
                    return Message(
                        sender="DynatraceAgent",
                        receiver="Orchestrator",
                        content={"dynatrace_logs": logs_response},
                        message_type="dynatrace_logs_fetched"
                    )
                else:
                    return Message(
                        sender="DynatraceAgent",
                        receiver="Orchestrator",
                        content={"error": f"Failed to query Dynatrace logs: {logs_response['error']}"},
                        message_type="dynatrace_error"
                    )
            else:
                return Message(
                    sender="DynatraceAgent",
                    receiver="Orchestrator",
                    content={"error": "query not provided for query_dynatrace_logs_request"},
                    message_type="dynatrace_error"
                )
        else:
            return Message(
                sender="DynatraceAgent",
                receiver="Orchestrator",
                content={"error": f"Unknown message type: {input_message.message_type}"},
                message_type="dynatrace_error"
            )

if __name__ == "__main__":
    # Example usage (for testing the agent in isolation)
    dynatrace_agent = DynatraceAgent()
    
    # Test query request
    query_msg = Message(
        sender="Test",
        receiver="DynatraceAgent",
        content={"query": "fetch logs | filter (matchesPhrase(content, \"ABC123\"))"},
        message_type="query_dynatrace_logs_request"
    )
    response = dynatrace_agent.process_message(query_msg, Context())
    print(f"Query Response: {response.content}")