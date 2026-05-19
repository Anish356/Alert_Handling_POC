# LangGraph Alert Workflow API

A dynamic alert remediation and diagnostics platform built using LangGraph, FastAPI, Docker, and Python.

This project receives monitoring alerts, dynamically routes them to the correct remediation flow, connects to customer-specific Docker environments, executes remediation scripts inside containers, and returns execution results through REST APIs.

---

# Features

- LangGraph-based workflow orchestration
- Dynamic flow routing
- Customer-specific environment resolution
- Docker container script execution
- FastAPI REST APIs
- Config-driven alert mapping
- Execution logging
- Workflow graph generation
- Auto-loaded remediation flows
- Structured execution tracking
- LangSmith tracing integration
- Multi-customer environment handling

---

# Project Structure

```bash
project/
│
├── AlphineOS/
│
├── config/
│   ├── env_config.json
│   └── alert_action_cfg.json
│
├── Graph/
│   └── graph.png
│
├── logs/
│
├── scripts/
│   ├── infrastructure/
│   ├── kubernetes/
│   ├── network/
│   └── services/
│
├── Utility/
│   └── logger.py
│
├── langgraph-env/
│
├── __pycache__/
│
├── AgentAPI.py
├── Agents.py
├── AgentWorkflow.py
├── requirements.txt
├── .env
├── .gitignore
├── README.md
└── installation.md
```

---

# Core Modules

| File/Folder | Purpose |
|---|---|
| AgentWorkflow.py | Main LangGraph workflow |
| Agents.py | Diagnostic and remediation flows |
| AgentAPI.py | FastAPI application |
| config/ | Environment and alert mappings |
| scripts/ | Shell scripts executed inside containers |
| logs/ | Runtime logs |
| Graph/ | Workflow graph image |

---

# Script Categories

| Folder | Purpose |
|---|---|
| scripts/infrastructure/ | Infrastructure remediation scripts |
| scripts/kubernetes/ | Kubernetes troubleshooting scripts |
| scripts/network/ | Network diagnostic scripts |
| scripts/services/ | Service health scripts |

---

# Workflow Architecture

```text
Alert Received
       |
       v
route_model
       |
       v
fetch_environment_details_node
       |
       v
identify_alert_action_node
       |
       v
Dynamic Flow Routing
       |
       v
login_node
       |
       v
script_executed_node
       |
       v
END
```
# Workflow Graph

The workflow graph is automatically generated using LangGraph and stored inside:

```bash
Graph/graph.png
```

The graph visually represents the execution flow of the alert remediation pipeline.

---

## Workflow Execution Flow

```text
                          +----------------+
                          |  route_model   |
                          +----------------+
                                   |
                                   v
             +--------------------------------------+
             | fetch_environment_details_node       |
             +--------------------------------------+
                                   |
                    access_verified == True
                                   |
                                   v
             +--------------------------------------+
             | identify_alert_action_node           |
             +--------------------------------------+
                                   |
                                   v
                     +------------------------+
                     |     agent_router       |
                     +------------------------+
                                   |
        ---------------------------------------------------
        |                    |                |            |
        v                    v                v            v
+----------------+  +----------------+ +----------------+ +----------------+
| infrastructure |  | service_health | | network_diag   | | application    |
| _diagnostic    |  | _flow          | | _flow          | | _flow          |
+----------------+  +----------------+ +----------------+ +----------------+
        \                    |                |            /
         \                   |                |           /
          \__________________|________________|__________/
                                   |
                                   v
                         +----------------+
                         |   login_node   |
                         +----------------+
                                   |
                                   v
                    +-----------------------------+
                    | script_executed_node        |
                    +-----------------------------+
                                   |
                                   v
                                +------+
                                | END  |
                                +------+
```

---

## Graph Generation

The graph is generated automatically during workflow initialization:

```python
workflow.save_graph()
```

Generated file:

```bash
Graph/graph.png
```


---

# Workflow Nodes

## route_model

Initial workflow entry node.

---

## fetch_environment_details_node

Fetches:

- Customer information
- Environment
- Host details
- Access verification

using:

```bash
config/env_config.json
```

The workflow dynamically identifies the correct customer container and environment before remediation execution.

---

## identify_alert_action_node

Identifies remediation action and scripts using:

```bash
config/alert_action_cfg.json
```

---

## login_node

Verifies Docker container connectivity before execution.

---

## script_executed_node

Executes remediation scripts inside customer-specific Docker containers.

---

# Customer Environment Mapping

The workflow dynamically maps customers to their dedicated environments and containers.

Example:

```json
[
  {
    "customer_name": "LBL",
    "env": "PROD",
    "host": "gcp-lblcsw-sn8cs.cloud.eu"
  },
  {
    "customer_name": "HBI",
    "env": "PROD",
    "host": "gcp-hbi-prod.cloud.com"
  },
  {
    "customer_name": "ITFX",
    "env": "PROD",
    "host": "gcp-itfx-prod.cloud.com"
  },
  {
    "customer_name": "ICJ1",
    "env": "PROD",
    "host": "gcp-icj1.cloud.com"
  }
]
```

Each workflow dynamically connects to the correct Docker container based on:

- Customer name
- Environment
- Host mapping

---

# Multi-Environment Support

Supported customer environments include:

| Customer | Environment | Host |
|---|---|---|
| LBLL | PROD | gcp-lblcsw-sn8633cs.cloud.eu |
| BRDL | PROD | gcp-brdooiv-p099.cloud.com |
| HBIL | PROD | gcp-hbi6-prod.cloud.com |
| WASL | PROD | gcp-wasl5-prod.cloud.com |


---

# Available Flows

## infrastructure_diagnostic_flow

Handles infrastructure diagnostics and remediation.

---

## service_health_flow

Performs service-level diagnostics and health checks.

---

## network_diagnostics_flow

Handles network troubleshooting and validation.

---

## application_diagnostics_flow

Performs application-level diagnostics.

---

# Dynamic Agent Loading

Flows are dynamically loaded from:

```python
AVAILABLE_AGENTS = {
    getattr(Agents, name).name: getattr(Agents, name)
    for name in dir(Agents)
    if hasattr(getattr(Agents, name), "invoke")
}
```

---

# Docker-Based Script Execution

Scripts are executed inside running Docker containers using:

```bash
docker exec -i <container_name> sh -s
```

Example containers:

```bash
gcp-lblcsw-sn86cs.cloud.eu
gcp-hbi-prod.cloud.com
gcp-itfx-prod.cloud.com
gcp-icj1.cloud.com
```

---

# Configuration Files

## Environment Configuration

File:

```bash
config/env_config.json
```

Example:

```json
[
  {
    "customer_name": "EK",
    "host": "gcp-ek-prod.cloud.com",
    "env": "PROD"
  }
]
```

---

## Alert Action Configuration

File:

```bash
config/alert_action_cfg.json
```

Example:

```json
[
  {
    "agent": "infrastructure_diagnostic_flow",
    "action": "cleanup_volume",
    "script_path": "scripts/kubernetes/cleanup_k8s_volume.sh"
  }
]
```

---

# Environment Variables

Create `.env` file:

```env
# =====================================================
# LANGSMITH
# =====================================================
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_api_key
LANGCHAIN_PROJECT=alert-workflow
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com


---

# API Endpoints

## Health Check

```http
GET /health
```

Response:

```json
{
  "status": "healthy"
}
```

---

## Root API

```http
GET /
```

Response:

```json
{
  "message": "LangGraph Alert Workflow API Running"
}
```

---

## Workflow Graph

```http
GET /graph
```

Returns workflow PNG image.

---

## Execute Alert Workflow

```http
POST /alerts
```

Example Request:

```json
{
  "success": true,
  "data": {
    "customer": "EK",
    "source": "New Relic",
    "service": "Kubernetes",
    "alert_code": "CXE701-0200",
    "environment": "PROD",
    "host": null,
    "issue": "k8s Volume is almost full",
    "alert_type": "Type6",
    "severity": "critical"
  },
  "agent_route": "Type6_critical_escalation_agent",
  "error": null,
  "warnings": []
}
```

---

# Sample Response

```json
{
  "status": "success",
  "message": "Alert processed successfully",
  "workflow_response": {}
}
```

---

# Logging

The application stores workflow execution logs dynamically inside:

```bash
logs/
```

Example log file:

```bash
2026-05-19T12-14-59_gcp-brdooiv-p08_cloud_com.log
```

Log filename format:

```text
<Timestamp>_<Host>_<Environment>.log
```

---

# Workflow Graph Generation

Workflow graph is auto-generated and stored in:

```bash
Graph/graph.png
```

---

# requirements.txt

Recommended dependencies:

```txt
fastapi
uvicorn
langgraph
langchain
python-dotenv
pydantic
typing_extensions
grandalf
```

---

# Run Application

Start FastAPI server:

```bash
uvicorn AgentAPI:app --reload
```

Application URL:

```bash
http://127.0.0.1:8010
```

---

# Test APIs

## Health API

```bash
curl http://127.0.0.1:8010/health
```

---

## Workflow API

```bash
curl -X POST http://127.0.0.1:8010/alerts \
-H "Content-Type: application/json" \
-d '{
  "success": true,
  "data": {
    "customer": "EK",
    "source": "New Relic",
    "service": "Kubernetes",
    "alert_code": "CXE701-0200",
    "environment": "PROD",
    "host": null,
    "issue": "k8s Volume is almost full",
    "alert_type": "Type6",
    "severity": "critical"
  },
  "agent_route": "Type6_critical_escalation_agent",
  "error": null,
  "warnings": []
}'
```

---

# Docker Requirement

Docker must be installed and running.

Verify installation:

```bash
docker --version
docker ps
```

---

# Technologies Used

- Python
- FastAPI
- LangGraph
- LangChain
- Docker
- Uvicorn
- LangSmith

---

