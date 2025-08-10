import os
from dotenv import load_dotenv

load_dotenv()

def get_auth_header(token_name: str) -> dict:
    """Retrieves the appropriate auth token from environment variables."""
    token = os.getenv(token_name)
    if not token:
        raise ValueError(f"Auth token '{token_name}' not found in .env file.")
    return {"Authorization": f"Basic {token}"}
