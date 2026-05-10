# Alert Interaction Automation using LangGraph + FastAPI

This project is an AI-driven infrastructure alert automation workflow built using:

- LangGraph
- FastAPI
- Docker
- LangChain Tools

The workflow receives infrastructure alerts through FastAPI, validates container accessibility, performs diagnostics, and executes remediation workflows automatically.

---

# Project Structure

```text
project/
│
├── AlphineOS/
├── AlphineOS2/
├── Graph/
│   └── graph.png
│
├── langgraph-env/
├── scripts/
├── __pycache__/
│
├── AgentAPI.py
├── Agents.py
├── AgentWorkflow.py
├── ReadMe.md
├── requirements.txt
```

---

# Workflow Architecture

```text
                FastAPI Alert
                       ↓
      check_environment_access_node
                       ↓
                 access_router
              ┌────────┴────────┐
              │                 │
           failed            router
              │                 │
             END          router_node
                                  ↓
                            issue_router
                     ┌────────┼────────┐
                     │        │        │
                  memory     cpu    unknown
                     │        │        │
               memory_node  cpu_node  unknown_node
                     │        │
                     └────┬───┘
                          ↓
               execute_script_node
                          ↓
                         END
```

---

# Workflow Logic

## Step 1 — Validate Container Accessibility

Workflow first validates whether the target container is accessible.

Example:

```bash
docker exec unix-container whoami
```

If container access fails:

```text
Workflow Ends
```

---

## Step 2 — Route Issue Type

Workflow checks:

```python
issue = state["issue"].lower()
```

Supported alert types:

- Memory alerts
- CPU alerts

---

## Step 3 — Execute Diagnostics

### Memory Diagnostics

```bash
docker exec unix-container free -h
```

### CPU Diagnostics

```bash
docker exec unix-container top -b -n 1
```

---

## Step 4 — Execute Remediation Script

If diagnostics succeed:

```text
execute_script_node
```

is triggered automatically.

---

# Docker Image Setup

This project uses a custom Alpine Linux Docker image with monitoring utilities installed.

## Dockerfile

```dockerfile
FROM alpine:latest

RUN apk add --no-cache \
    bash \
    procps \
    coreutils

CMD ["tail", "-f", "/dev/null"]
```

---

# Installed Packages

| Package | Purpose |
|---|---|
| bash | Shell access |
| procps | top, ps commands |
| coreutils | Linux utilities |

---

# Step 1 — Install Docker Desktop

Download Docker Desktop:

## Windows

https://www.docker.com/products/docker-desktop/

Install Docker Desktop and ensure Docker Engine is running.

---

# Step 2 — Verify Docker Installation

```bash
docker --version
```

Expected Output:

```text
Docker version 27.x.x
```

---

# Step 3 — Build Docker Image

Run the following command inside the project directory where the Dockerfile exists:

```bash
docker build -t unix-agent-env .
```

Verify image creation:

```bash
docker images
```

Expected Output:

```text
REPOSITORY        TAG       IMAGE ID
unix-agent-env    latest    xxxxxx
```

---

# Step 4 — Create unix-container

```bash
docker run -d \
--name unix-container \
unix-agent-env
```

---

# Step 5 — Create gcp-container

```bash
docker run -d \
--name gcp-container \
unix-agent-env
```

---

# Step 6 — Verify Running Containers

```bash
docker ps
```

Expected Output:

```text
CONTAINER ID   IMAGE             NAMES
xxxxxx         unix-agent-env    unix-container
xxxxxx         unix-agent-env    gcp-container
```

---

# Step 7 — Test Container Access

## Test unix-container

```bash
docker exec unix-container whoami
```

Expected Output:

```text
root
```

---

## Test gcp-container

```bash
docker exec gcp-container whoami
```

Expected Output:

```text
root
```

---

# Python Environment Setup

## Step 1 — Create Virtual Environment

```bash
python -m venv langgraph-env
```

---

## Step 2 — Activate Virtual Environment

### Windows PowerShell

```bash
.\langgraph-env\Scripts\activate
```

---

## Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

---

# requirements.txt

```text
fastapi
uvicorn
langgraph
langchain
pydantic
docker
```

---

# Run FastAPI Application

Start API server:

```bash
uvicorn AgentAPI:app --reload --port 8010
```

Application URL:

```text
http://127.0.0.1:8010
```

Swagger UI:

```text
http://127.0.0.1:8010/docs
```

---

# API Endpoints

# Health Check

## Request

```http
GET /health
```

## Response

```json
{
  "status": "healthy"
}
```

---

# Process Alert

## Request

```http
POST /alerts
```

## Sample Payload

```json
{
  "customer": "AlphineOS",
  "source": "DockerMonitor",
  "service": "unix-container",
  "alert_code": "MEM_HIGH",
  "environment": "dev",
  "host": "unix-container",
  "issue": "Memory usage exceeded threshold"
}
```

---

# Example API Success Response

```json
{
  "status": "success",
  "message": "Alert processed successfully"
}
```

---

# Example API Failure Response

```json
{
  "status": "failed",
  "message": "Container execution failed"
}
```

---

# Docker Commands

## View Running Containers

```bash
docker ps
```

---

## Stop Container

```bash
docker stop unix-container
```

---

## Start Container

```bash
docker start unix-container
```

---

## Remove Container

```bash
docker rm -f unix-container
```

---

## View Docker Images

```bash
docker images
```

---

# Graph Visualization

Workflow graph image is automatically generated:

```text
Graph/graph.png
```

API Endpoint:

```http
GET /graph
```

---

# Current Workflow Nodes

| Node | Purpose |
|---|---|
| check_environment_access_node | Validate container accessibility |
| router_node | Detect issue type |
| memory_node | Run memory diagnostics |
| cpu_node | Run CPU diagnostics |
| execute_script_node | Execute remediation |
| unknown_node | Unsupported alert handling |

---

# Technologies Used

- Python
- FastAPI
- LangGraph
- LangChain
- Docker
- Uvicorn

---


# Author

Anish Yadav