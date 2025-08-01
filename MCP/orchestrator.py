from MCP.mcp_core import Message, Context
from Coding.src.agent import get_specification_refinement, get_prioritization, generate_test_cases, TestCases
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'LogandRCA agent'))
from agent import LogRCAAgent # This assumes agent.py is directly in 'LogandRCA agent'
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    print("Starting MCP Orchestrator...")

    # Initialize agents
    # Note: Adjust paths and initialization parameters as per your actual agent implementations
    coding_agent = {
        "generate_test_cases": generate_test_cases,
        "get_specification_refinement": get_specification_refinement,
        "get_prioritization": get_prioritization
    }
    log_rca_agent = LogRCAAgent(
        neo4j_uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        neo4j_user=os.getenv("NEO4J_USER", "neo4j"),
        neo4j_password=os.getenv("NEO4J_PASSWORD", "password")
    )

    # Initialize a shared context
    shared_context = Context(
        input_data={
            "user_story": "As a user, I want to be able to log in to the system so that I can access my personalized dashboard.",
            "development_considerations": "Implement secure authentication using OAuth2. Handle invalid credentials gracefully. Ensure quick response times for login requests."
        },
        shared_analysis_results={}
    )

    print("\n--- Interaction 1: Coding Agent generates Test Cases ---")
    # Create a message for the Coding Agent
    coding_input_message = Message(
        sender="Orchestrator",
        receiver="CodingAgent",
        content={
            "user_story": shared_context.input_data["user_story"],
            "development_considerations": shared_context.input_data["development_considerations"]
        },
        message_type="generate_test_cases_request"
    )

    # Coding Agent processes the message
    test_cases_response_message = coding_agent["generate_test_cases"](
        input_message=coding_input_message,
        context=shared_context
    )

    print(f"Coding Agent Response Type: {test_cases_response_message.message_type}")
    if test_cases_response_message.message_type == "test_cases_generated":
        generated_test_cases_dict = test_cases_response_message.content.get("test_cases")
        if generated_test_cases_dict:
            # Convert dict back to TestCases Pydantic model for easier access if needed
            generated_test_cases = TestCases(**generated_test_cases_dict)
            print(f"Generated {len(generated_test_cases.test_cases)} Test Cases.")
            # Example: Print the first test case description
            if generated_test_cases.test_cases:
                print(f"First Test Case Description: {generated_test_cases.test_cases[0].description}")
                # Store in context for potential use by other agents
                shared_context.shared_analysis_results["latest_test_cases"] = generated_test_cases_dict
        else:
            print("No test cases found in the response.")
    else:
        print(f"Error from Coding Agent: {test_cases_response_message.content}")

    print("\n--- Interaction 2: LogRCA Agent analyzes a query based on a test case ---")
    # Assuming we want to query the LogRCA agent about a potential issue related to a test case
    query_for_log_rca = "What is the root cause of login failures related to '"
                        + shared_context.input_data["user_story"] + "' and the test case: '"
                        + (generated_test_cases.test_cases[0].description if generated_test_cases.test_cases else "") + "'?"

    log_rca_input_message = Message(
        sender="Orchestrator",
        receiver="LogRCAAgent",
        content={
            "query": query_for_log_rca
        },
        message_type="root_cause_analysis_request"
    )

    # LogRCA Agent processes the message
    root_cause_response_message = log_rca_agent.query_agent(
        input_message=log_rca_input_message,
        context=shared_context
    )

    print(f"LogRCA Agent Response Type: {root_cause_response_message.message_type}")
    if root_cause_response_message.message_type == "root_cause_analysis":
        root_cause = root_cause_response_message.content.get("root_cause_hypothesis")
        confidence = root_cause_response_message.content.get("confidence_score")
        print(f"Root Cause Hypothesis: {root_cause}")
        print(f"Confidence Score: {confidence}")
    else:
        print(f"Error from LogRCA Agent: {root_cause_response_message.content}")

    print("\nOrchestration complete.")

if __name__ == "__main__":
    main()
