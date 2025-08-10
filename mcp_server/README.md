# Modular Context-Orchestrator (MCP) Server

A FastAPI server to dynamically route requests to internal services with template-based payloads and dynamic authentication.

## Features

- **Dynamic Routing**: Calls different backend services based on the request payload.
- **Template-Based Payloads**: Uses predefined YAML templates for request bodies, allowing for easy overrides.
- **Service-Specific Auth**: Injects Basic Authentication headers based on the target service.
- **Copilot Tool Integration**: Exposes the `/invoke` endpoint as a tool for GitHub Copilot Chat.

## Project Structure

```
mcp_server/
├── main.py                      # Entrypoint - FastAPI app
├── config.yaml                  # Service base URLs + auth config
├── invoke.py                    # Logic to build request and call target service
├── templates/
│   └── request_templates.yaml   # Static request bodies per service + endpoint
├── auth/
│   └── auth_handler.py          # Service-based dynamic auth resolver
├── tools/
│   ├── library.py               # Tool-specific logic (if needed)
│   └── cafeteria.py
├── langgraph_flow.py            # Placeholder for LangGraph (future)
├── manifest/
│   └── copilot-tools.json       # Tool schema for VS Code Copilot Chat
├── requirements.txt             # Python dependencies
├── .env.example                 # Example env file for service credentials
└── README.md
```

## Setup and Running

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Configure Environment**:
    Copy `.env.example` to a new file named `.env` and add your service credentials.
    ```bash
    cp .env.example .env
    ```

3.  **Run the Server**:
    ```bash
    uvicorn main:app --host 0.0.0.0 --port 9000 --reload
    ```
    The server will be available at `http://localhost:9000`.

## VS Code Copilot Tool Setup

To use this server as a tool in GitHub Copilot Chat, add the following to your VS Code `settings.json`:

```json
"copilot.tools": {
    "mcp-invoke": {
        "url": "http://localhost:9000/invoke",
        "manifest": "./mcp_server/manifest/copilot-tools.json"
    }
}
```
