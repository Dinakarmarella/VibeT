import os
from dotenv import load_dotenv

# Ensure project root is in sys.path
import sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

from MCP.mcp_core import Message, Context
from agent import get_specification_refinement, get_prioritization, generate_test_cases, TestCases
from agent import LogRCAAgent
from jira_agent import JiraAgent
from DJ_SLM.dynatrace_agent import DynatraceAgent

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
    jira_agent = JiraAgent()
    dynatrace_agent = DynatraceAgent()

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
    query_for_log_rca = "What is the root cause of login failures related to '"                         + shared_context.input_data["user_story"] + "' and the test case: '"                         + (generated_test_cases.test_cases[0].description if generated_test_cases.test_cases else "") + "'?"

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

    print("\n--- Interaction 3: SLM-Based Defect Automation ---")
    # Simulate a new Sev1 Jira issue coming in
    new_jira_issue_id = "DEF-789" # This would typically come from a Jira webhook or polling

    # 1. Fetch Jira Issue using JiraAgent
    fetch_jira_msg = Message(
        sender="Orchestrator",
        receiver="JiraAgent",
        content={"issue_id": new_jira_issue_id},
        message_type="fetch_jira_issue_request"
    )
    jira_fetch_response = jira_agent.process_message(fetch_jira_msg, shared_context)

    defect_description = ""
    if jira_fetch_response.message_type == "jira_issue_fetched":
        jira_issue = jira_fetch_response.content.get("jira_issue")
        defect_description = jira_issue.get("description", "")
        print(f"Fetched Jira issue: {jira_issue.get('summary')} - {defect_description}")
    else:
        print(f"Error fetching Jira issue: {jira_fetch_response.content.get('error', 'Unknown error')}")
        print("Using a default description for processing.")
        defect_description = "Simulated defect: User cannot log in to the application due to an authentication error."

    # Load SLM automation components
    from slm_automation import load_data, initialize_embedding_model, load_faiss_index, create_faiss_index, process_defect
    historical_kb, keyword_team_map = load_data()
    model = initialize_embedding_model()
    if not os.path.exists(os.path.join(os.path.dirname(__file__), '..', 'DJ_SLM', 'faiss_index.bin')):
        faiss_index = create_faiss_index(historical_kb, model)
        print("FAISS index created and saved.")
    else:
        faiss_index = load_faiss_index()
        print("FAISS index loaded from file.")

    # Process the defect using the SLM automation logic
    assigned_team, resolution_steps = process_defect(defect_description, model, faiss_index, historical_kb, keyword_team_map)

    # 5. Update Jira ticket using JiraAgent
    update_payload = {
        "fields": {
            "assignee": {"name": assigned_team},
            "comment": [{
                "add": {
                    "body": f"Automated triage: Assigned to {assigned_team}. Suggested action: {resolution_steps}"
                }
            }]
        }
    }
    update_jira_msg = Message(
        sender="Orchestrator",
        receiver="JiraAgent",
        content={"issue_id": new_jira_issue_id, "updates": update_payload},
        message_type="update_jira_issue_request"
    )
    jira_update_response = jira_agent.process_message(update_jira_msg, shared_context)
    print(f"Jira Update Result: {jira_update_response.content}")

    print("\nOrchestration complete.")

if __name__ == "__main__":
    main()
