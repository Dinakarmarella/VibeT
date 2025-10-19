import sys
import jira_agent
import slm_automation

def main():
    """Main orchestration function."""
    if len(sys.argv) < 2:
        print("Usage: python orchestrator.py <JIRA_ISSUE_ID>")
        sys.exit(1)

    jira_issue_id = sys.argv[1]

    print(f"--- Starting analysis for Jira issue: {jira_issue_id} ---")

    # 1. Fetch issue details from Jira
    issue_details = jira_agent.get_issue(jira_issue_id)
    if not issue_details:
        print(f"Could not retrieve details for {jira_issue_id}. Exiting.")
        sys.exit(1)

    # Extract summary and description
    summary = issue_details.get('fields', {}).get('summary', '')
    description_obj = issue_details.get('fields', {}).get('description')
    
    # Jira description is a complex object, we need to parse it to text
    description_text = ""
    if description_obj:
        for content_block in description_obj.get('content', []):
            for content_item in content_block.get('content', []):
                if content_item.get('type') == 'text':
                    description_text += content_item.get('text', '') + "\n"

    if not description_text:
        description_text = summary # Fallback to summary if description is empty

    print(f"\n--- Analyzing issue: {summary} ---")

    # 2. Get analysis from the SLM automation module
    # We are using the mock function from slm_automation for this example
    assigned_team, suggested_resolution = slm_automation.analyze_new_defect_mock(description_text)

    print(f"\n--- SLM Analysis Complete ---")
    print(f"Suggested Team: {assigned_team}")
    print(f"Suggested Resolution: {suggested_resolution}")

    # 3. Update the Jira issue with the analysis
    comment = (
        f"**Automated SLM Analysis:**\n\n"
        f"**Suggested Team:** {assigned_team}\n"
        f"**Suggested Resolution:**\n{suggested_resolution}"
    )

    print(f"\n--- Updating Jira issue {jira_issue_id} ---")
    jira_agent.update_issue(jira_issue_id, comment, assigned_team)

    print(f"\n--- Process for {jira_issue_id} complete. ---")

if __name__ == "__main__":
    main()