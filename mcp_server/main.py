from fastapi import FastAPI, Request
from pydantic import BaseModel
from invoke import invoke_service

app = FastAPI(
    title="Modular Context-Orchestrator (MCP) Server",
    description="A FastAPI server to dynamically route requests to internal services with template-based payloads.",
    version="1.0.0"
)

class InvokeRequest(BaseModel):
    service: str
    endpoint: str
    template_id: str
    payload_overrides: dict

@app.post("/invoke", summary="Invoke an Internal Service")
def invoke(req: InvokeRequest):
    """
    Core endpoint to proxy requests to backend services.
    - **service**: The name of the target service (e.g., 'library', 'cafeteria').
    - **endpoint**: The API endpoint path (e.g., '/add_user', '/order_meal').
    - **template_id**: The ID of the request template to use.
    - **payload_overrides**: A dictionary of values to override in the template.
    """
    result = invoke_service(
        req.service, req.endpoint, req.template_id, req.payload_overrides
    )
    return {"result": result}

@app.get("/", summary="Health Check")
def read_root():
    return {"status": "MCP Server is running"}
