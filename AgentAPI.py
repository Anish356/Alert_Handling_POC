import os

from datetime import datetime

from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, PlainTextResponse

from AgentWorkflow import workflow

from Utility.logger import setup_logger


# =========================================================
# LOAD ENV VARIABLES
# =========================================================
load_dotenv()


# =========================================================
# LOGGER
# =========================================================
logger = setup_logger(__name__)


# =========================================================
# FASTAPI APP
# =========================================================
app = FastAPI(
    title="LangGraph Alert Workflow API",
    version="1.0.0",
    description="Consumes alert data and executes LangGraph workflow"
)


# =========================================================
# HEALTH CHECK
# =========================================================
@app.get("/health")
async def health():

    logger.info("Health check endpoint called")

    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


# =========================================================
# ROOT API
# =========================================================
@app.get("/")
async def root():

    logger.info("Root endpoint called")

    return {
        "message": "LangGraph Alert Workflow API Running",
        "version": "1.0.0"
    }


# =========================================================
# GRAPH IMAGE API
# =========================================================
@app.get("/graph")
async def get_graph():

    logger.info("Graph endpoint called")

    file_path = "Graph/graph.png"

    if not os.path.exists(file_path):

        logger.warning("Graph image not found")

        return PlainTextResponse(
            content="No graph found",
            status_code=404
        )

    logger.info("Returning graph image")

    return FileResponse(
        path=file_path,
        media_type="image/png"
    )


# =========================================================
# MAIN WORKFLOW ENDPOINT
# =========================================================
@app.post("/alerts")
async def create_alert(payload: dict):



    logger.info("Received alert")

    try:

        # =================================================
        # EXTRACT ALERT DATA
        # =================================================
        alert_data = payload

        logger.info("Sending data to LangGraph workflow")

        #logger.info(f"Workflow Input: {alert_data}")

        # =================================================
        # EXECUTE WORKFLOW
        # =================================================
        response = workflow.run(alert_data) # <------ 
       # print(response)

        logger.info("Workflow execution completed")

        # =================================================
        # SUCCESS RESPONSE
        # =================================================
        return {

            "status": "success",

            "message": "Alert processed successfully",

            "workflow_response": response
        }

    except Exception as e:

        logger.exception("Workflow execution failed")

        raise HTTPException(
            status_code=500,
            detail={
                "status": "failed",
                "message": "Workflow execution failed",
                "error": str(e)
            }
        )


# =========================================================
# RUN
# =========================================================
# uvicorn main:app --reload