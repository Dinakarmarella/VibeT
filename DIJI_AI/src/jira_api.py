import requests
import yaml
import os

config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.yaml")
config = yaml.safe_load(open(config_path))
JIRA_DOMAIN = config["jira"]["domain"]
AUTH = (config["jira"]["email"], config["jira"]["api_token"])

def fetch_closed_defects(jql="status=Closed"):
    url = f"https://{JIRA_DOMAIN}/rest/api/3/search"
    params = {"jql": jql, "maxResults": 100}
    r = requests.get(url, params=params, auth=AUTH)
    r.raise_for_status()
    return r.json()

def post_comment(issue_key, body):
    url = f"https://{JIRA_DOMAIN}/rest/api/3/issue/{issue_key}/comment"
    headers = {"Content-Type":"application/json"}
    payload = {"body": body}
    r = requests.post(url, json=payload, auth=AUTH, headers=headers)
    r.raise_for_status()
    return r.json()
