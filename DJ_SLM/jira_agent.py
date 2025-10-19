import os
import requests
import base64
from dotenv import load_dotenv

load_dotenv()

JIRA_API_URL = os.getenv("JIRA_API_URL")
JIRA_USER_EMAIL = os.getenv("JIRA_USER_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")

def get_auth_header():
    """Creates the Basic Auth header for Jira API requests."""
    auth_string = f"{JIRA_USER_EMAIL}:{JIRA_API_TOKEN}"
    encoded_auth_string = base64.b64encode(auth_string.encode('utf-8')).decode('utf-8')
    return f"Basic {encoded_auth_string}"

def get_issue(issue_id):
    """Fetches details for a specific Jira issue."""
    url = f"{JIRA_API_URL}/issue/{issue_id}"
    headers = {
        "Accept": "application/json",
        "Authorization": get_auth_header()
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status() # Raises an exception for bad status codes (4xx or 5xx)
        print(f"Successfully fetched issue {issue_id}")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching issue {issue_id}: {e}")
        return None

def update_issue(issue_id, comment, team_name):
    """Adds a comment and reassigns a Jira issue."""
    # Note: Re-assigning requires knowing the user account ID for the team.
    # This is a placeholder and would need a mapping from team_name to accountId.
    # For now, we will just add a comment.
    
    comment_url = f"{JIRA_API_URL}/issue/{issue_id}/comment"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": get_auth_header()
    }
    
    comment_payload = {
        "body": {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": comment
                        }
                    ]
                }
            ]
        }
    }

    try:
        response = requests.post(comment_url, headers=headers, json=comment_payload)
        response.raise_for_status()
        print(f"Successfully added comment to issue {issue_id}")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error adding comment to issue {issue_id}: {e}")
        return None