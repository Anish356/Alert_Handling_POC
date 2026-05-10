from fastapi import FastAPI
from fastapi.responses import FileResponse, PlainTextResponse
from pydantic import BaseModel
from datetime import datetime
import os
from dotenv import load_dotenv
import os
from AgentWorkflow import graph

load_dotenv() 
# ==========================================
# FASTAPI APP
# ==========================================
app = FastAPI(
    title="Alert Interaction API",
    version="1.0.0"
)


# ==========================================
# REQUEST MODEL
# ==========================================
class AlertPayload(BaseModel):
    customer: str
    source: str
    service: str
    alert_code: str
    environment: str
    host: str
    issue: str


# ==========================================
# HEALTH CHECK
# ==========================================
@app.get("/health")
async def health():

    return {
        "status": "healthy",
        "timestamp": datetime.utcnow()
    }


# ==========================================
# ALERT API
# ==========================================
@app.post("/alerts")
async def create_alert(payload: AlertPayload):

    try:

        # ==========================================
        # RUN LANGGRAPH WORKFLOW
        # ==========================================
        response = graph.invoke(payload.model_dump())

        print("\n================ WORKFLOW RESPONSE ================")
        print(response)

        result = response.get("result", "")

        # ==========================================
        # FAILURE CASE
        # ==========================================
        if "'status': 'failed'" in result:

            return {
                "status": "failed",
                "message": "Container execution failed",
                "workflow_response": response
            }

        # ==========================================
        # SUCCESS CASE
        # ==========================================
        return {
            "status": "success",
            "message": "Alert processed successfully",
            "workflow_response": response
        }

    except Exception as e:

        return {
            "status": "failed",
            "message": "Workflow execution failed",
            "error": str(e)
        }


# ==========================================
# GRAPH IMAGE API
# ==========================================
@app.get("/graph")
async def get_graph():

    file_path = "Graph/graph.png"

    if not os.path.exists(file_path):

        return PlainTextResponse(
            content="No graph found",
            status_code=404
        )

    return FileResponse(
        path=file_path,
        media_type="image/png",
    )