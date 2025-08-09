

import os
from dotenv import load_dotenv
from slm_automation (
    load_data,
    initialize_embedding_model,
    load_faiss_index,
    create_faiss_index,
    process_defect
)
from jira_agent import fetch_jira_issue, update_jira_ticket

# Load environment variables from .env file
load_dotenv()

def main(issue_id):
    """
    Main orchestration function.
    
    Args:
        issue_id (str): The ID of the Jira issue to process.
    """
    print(f"--- Starting SLM Defect Automation for Issue: {issue_id} ---")

    # 1. Load all necessary data and models
    historical_kb, keyword_team_map = load_data()
    model = initialize_embedding_model()
    
    # Load or create the FAISS index
    base_dir = os.path.dirname(os.path.abspath(__file__))
    faiss_index_path = os.path.join(base_dir, 'faiss_index.bin')
    if os.path.exists(faiss_index_path):
        faiss_index = load_faiss_index()
        print("FAISS index loaded from file.")
    else:
        print("FAISS index not found. Creating and saving a new one.")
        faiss_index = create_faiss_index(historical_kb, model)
        print("FAISS index created and saved.")

    # 2. Fetch the Jira issue
    print(f"Fetching details for Jira issue: {issue_id}...")
    jira_issue = fetch_jira_issue(issue_id)

    if not jira_issue or "fields" not in jira_issue or not jira_issue["fields"].get("description"):
        print(f"Error: Could not fetch Jira issue {issue_id} or it has no description. Aborting.")
        return

    defect_description = jira_issue["fields"]["description"]
    print(f"Successfully fetched issue. Summary: {jira_issue['fields']['summary']}")

    # 3. Process the defect to get assignment and resolution
    print("Processing defect for team assignment and resolution steps...")
    assigned_team, resolution_steps = process_defect(
        defect_description,
        model,
        faiss_index,
        historical_kb,
        keyword_team_map
    )

    if not assigned_team or assigned_team == "Unassigned":
        print("Could not determine team assignment. Manual intervention required.")
        # Optionally, send a notification here
        return

    print(f"Triage complete. Assigned Team: {assigned_team}, Suggested Resolution: {resolution_steps}")

    # 4. Update the Jira ticket
    print(f"Updating Jira ticket {issue_id}...")
    update_payload = {
        "fields": {
            # Note: To assign a user in Jira, you may need 'accountId' instead of 'name'
            # This depends on your Jira instance configuration.
            # "assignee": {"name": assigned_team},
            "comment": [{
                "add": {
                    "body": f"Automated Triage Result:\n\n*Assigned Team:* {assigned_team}\n*Suggested Action:* {resolution_steps}"
                }
            }]
        }
    }
    
    update_result = update_jira_ticket(issue_id, update_payload)
    print(f"Jira update result: {update_result}")
    print(f"--- Automation process for Issue {issue_id} finished. ---")


if __name__ == "__main__":
    # This allows the script to be run from the command line with an issue ID
    # Example: python orchestrator.py DEF-123
    import sys
    if len(sys.argv) > 1:
        issue_to_process = sys.argv[1]
        main(issue_to_process)
    else:
        print("Please provide a Jira issue ID as a command-line argument.")
        # Example of running with a default test ID
        print("Running with default test issue 'DEF-789'.")
        main("DEF-789")

