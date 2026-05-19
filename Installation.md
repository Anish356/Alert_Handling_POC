# Installation Guide

This document explains how to install and run the LangGraph Alert Workflow API.

---

# Prerequisites

Install the following:

- Python 3.10+
- Docker Desktop / Docker Engine
- Git

---

# Clone Repository

```bash
git clone <your-repository-url>
cd <project-folder>
```

---

# Build Docker Image

Dockerfile is available inside:

```bash
AlphineOS/
```

Move into Docker directory:

```bash
cd AlphineOS
```

Build Docker image:

```bash
docker build -t alpineos-image .
```

Verify image:

```bash
docker images
```

Expected output:

```bash
alpineos-image
```

---

# Create Customer Containers

Run containers using the generated image.

---

## LBL Container

```bash
docker run -dit \
--name gcp-lblcsw-sn86cs.cloud.eu \
alpineos-image
```

---

## HBI Container

```bash
docker run -dit \
--name gcp-hbi-prod.cloud.com \
alpineos-image
```

---

## ITFX Container

```bash
docker run -dit \
--name gcp-itfx-prod.cloud.com \
alpineos-image
```

---

## ICJ1 Container

```bash
docker run -dit \
--name gcp-icj1.cloud.com \
alpineos-image
```

---

# Verify Running Containers

```bash
docker ps
```

Expected containers:

```bash
gcp-lblcsw-sn86cs.cloud.eu
gcp-hbi-prod.cloud.com
gcp-itfx-prod.cloud.com
gcp-icj1.cloud.com
```

---

# Docker Management Commands

## Start Container

```bash
docker start gcp-lblcsw-sn86cs.cloud.eu
```

---

## Stop Container

```bash
docker stop gcp-lblcsw-sn86cs.cloud.eu
```

---

## Remove Container

```bash
docker rm -f gcp-lblcsw-sn86cs.cloud.eu
```

---

## Access Container

```bash
docker exec -it gcp-lblcsw-sn86cs.cloud.eu /bin/bash
```

---

# Return To Project Root

```bash
cd ..
```

---

# Create Python Virtual Environment

## Windows

```powershell
python -m venv langgraph-env
langgraph-env\Scripts\activate
```

---

## Linux / Mac

```bash
python3 -m venv langgraph-env
source langgraph-env/bin/activate
```

---

# Install Python Libraries

```bash
pip install -r requirements.txt
```

---

# requirements.txt

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

# Configure Environment Variables

Create `.env` file:

```env
# =====================================================
# LANGSMITH
# =====================================================
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_api_key
LANGCHAIN_PROJECT=alert-workflow
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
```

---

# Configure Environment Mapping

Create:

```bash
config/env_config.json
```

Example:

```json
[
  {
    "customer_name": "LBL",
    "env": "PROD",
    "host": "gcp-lblcsw-sn86cs.cloud.eu"
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

---

# Configure Alert Action Mapping

Create:

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

# Project Script Structure

```bash
scripts/
├── infrastructure/
├── kubernetes/
├── network/
└── services/
```

---

# Run FastAPI Application

Activate virtual environment first.

---

## Windows

```powershell
langgraph-env\Scripts\activate
```

---

## Linux / Mac

```bash
source langgraph-env/bin/activate
```

---

# Start API Server

```bash
python -m uvicorn AgentAPI:app --host 127.0.0.1 --port 8010
```

OR

```bash
uvicorn AgentAPI:app --reload --host 127.0.0.1 --port 8010
```

---

# API URLs

Application:

```bash
http://127.0.0.1:8010
```

Swagger UI:

```bash
http://127.0.0.1:8010/docs
```

ReDoc:

```bash
http://127.0.0.1:8010/redoc
```

---

# Available APIs

| Method | Endpoint | Description |
|---|---|---|
| GET | / | Root API |
| GET | /health | Health Check |
| GET | /graph | Workflow Graph |
| POST | /alerts | Execute Alert Workflow |

---

# Test APIs Using Swagger

Open:

```bash
http://127.0.0.1:8010/docs
```

Steps:

1. Open `POST /alerts`
2. Click `Try it out`
3. Paste payload
4. Click `Execute`

---

# Sample Alert Payload

```json
{
  "success": true,
  "data": {
    "customer": "LBL",
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

# Test API Using CURL

```bash
curl -X POST http://127.0.0.1:8010/alerts \
-H "Content-Type: application/json" \
-d '{
  "success": true,
  "data": {
    "customer": "LBL",
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

# Workflow Graph

Generated graph:

```bash
Graph/graph.png
```

Access API:

```http
GET /graph
```

---

# Logging

Logs are stored inside:

```bash
logs/
```

Example:

```bash
2026-05-19T12-14-59_gcp-brdooiv-p08_cloud_com.log
```

---

# Common Issues

## Docker Container Not Found

Check running containers:

```bash
docker ps
```

---

## Container Stopped

Start container:

```bash
docker start <container_name>
```

---

## Permission Denied

Run terminal as Administrator or use sudo.

---

## Python Dependency Missing

Install again:

```bash
pip install -r requirements.txt
```

---

# Technologies Used

- Python
- FastAPI
- LangGraph
- LangChain
- Docker
- LangSmith
- Uvicorn

---

# Installation Complete

Your LangGraph Alert Workflow API is now ready to execute customer-specific remediation workflows.