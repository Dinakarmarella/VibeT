import yaml
import requests
from auth.auth_handler import get_auth_header

def invoke_service(service: str, endpoint: str, template_id: str, payload_overrides: dict):
    """Builds and sends a request to a target service."""
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)

    with open("templates/request_templates.yaml", "r") as f:
        templates = yaml.safe_load(f)

    base_url = config["services"][service]["base_url"]
    auth_token_name = config["services"][service]["auth"]
    template = templates[template_id]

    # Override template with payload
    template.update(payload_overrides)

    headers = {
        "Content-Type": "application/json",
        **get_auth_header(auth_token_name),
    }

    response = requests.post(f"{base_url}{endpoint}", json=template, headers=headers)
    return response.json()
