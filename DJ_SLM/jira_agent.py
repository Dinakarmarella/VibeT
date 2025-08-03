
import os
import requests
import base64
from dotenv import load_dotenv

load_dotenv()

JIRA_API_URL = os.getenv("JIRA_API_URL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_USER_EMAIL = os.getenv("JIRA_USER_EMAIL")

def get_jira_auth():
    return base64.b64encode(f'{JIRA_USER_EMAIL}:{JIRA_API_TOKEN}'.encode()).decode()

def fetch_jira_issue(issue_id):
    if not all([JIRA_API_URL, JIRA_API_TOKEN, JIRA_USER_EMAIL]):
        print("Jira API credentials not fully configured in .env. Using mock data.")
        return {
            "id": issue_id,
            "fields": {
                "summary": "Simulated Sev1 Defect",
                "description": f"This is a test defect for {issue_id}. It has some issues with authentication.",
                "status": {"name": "Open"},
                "assignee": None
            }
        }

    headers = {
        "Accept": "application/json",
        "Authorization": f"Basic {get_jira_auth()}"
    }
    url = f"{JIRA_API_URL}/issue/{issue_id}"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Jira issue {issue_id}: {e}")
        return None

def update_jira_ticket(issue_id, updates):
    if not all([JIRA_API_URL, JIRA_API_TOKEN, JIRA_USER_EMAIL]):
        print("Jira API credentials not fully configured in .env. Using mock update.")
        return {"status": "mock_success", "issue_id": issue_id, "updates": updates}

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Basic {get_jira_auth()}"
    }
    url = f"{JIRA_API_URL}/issue/{issue_id}"
    try:
        response = requests.put(url, headers=headers, json=updates)
        response.raise_for_status()
        return {"status": "success", "issue_id": issue_id, "response": response.json() if response.content else "No content"}
    except requests.exceptions.RequestException as e:
        print(f"Error updating Jira issue {issue_id}: {e}")
        return {"status": "failed", "error": str(e)}
