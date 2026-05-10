from typing import TypedDict
from langgraph.graph import StateGraph, END

from Agents import memory_check, cpu_check, enter_container


# ==========================================
# STATE
# ==========================================
class AlertState(TypedDict):
    customer: str
    source: str
    service: str
    alert_code: str
    environment: str
    host: str
    issue: str

    tool_used: str
    result: str
    container_status: str

    next_step: str


# ==========================================
# STEP 1:
# CHECK CONTAINER ACCESS
# ==========================================
def check_environment_access_node(state: AlertState):

    print("\n[CONTAINER NODE] Checking container accessibility")

    container_name = state["host"]

    output = enter_container.invoke({
        "container_name": container_name
    })

    print(output)

    state["tool_used"] = "enter_container"
    state["result"] = str(output)

    # Save container status
    if output.get("status") == "connected":
        state["container_status"] = "connected"
    else:
        state["container_status"] = "failed"

    return state


# ==========================================
# ACCESS ROUTER
# ==========================================
def access_router(state: AlertState):

    # If container access failed → END
    if state["container_status"] == "failed":
        return "failed"

    return "router"


# ==========================================
# ROUTER NODE
# ==========================================
def router_node(state: AlertState):

    print("\n[ROUTER NODE] Deciding issue type")

    issue = state["issue"].lower()

    if "memory" in issue:
        state["next_step"] = "memory"

    elif "cpu" in issue:
        state["next_step"] = "cpu"

    else:
        state["next_step"] = "unknown"

    return state


# ==========================================
# ISSUE ROUTER FUNCTION
# ==========================================
def issue_router(state: AlertState):

    return state["next_step"]


# ==========================================
# MEMORY NODE
# ==========================================
def memory_node(state: AlertState):

    print("\n[MEMORY NODE] Running memory tool")

    output = memory_check.invoke({
        "container_name": state["host"]
    })

    print(output)

    state["tool_used"] += " + memory_check"
    state["result"] += " | " + str(output)

    return state


# ==========================================
# CPU NODE
# ==========================================
def cpu_node(state: AlertState):

    print("\n[CPU NODE] Running CPU tool")

    output = cpu_check.invoke({
        "container_name": state["host"]
    })

    print(output)

    state["tool_used"] += " + cpu_check"
    state["result"] += " | " + str(output)

    return state


# ==========================================
# UNKNOWN NODE
# ==========================================
def unknown_node(state: AlertState):

    print("\n[UNKNOWN NODE] No matching issue found")

    state["tool_used"] += " + unknown"
    state["result"] += " | No matching issue type found"

    return state


# ==========================================
# EXECUTE SCRIPT NODE
# ==========================================
def execute_script_node(state: AlertState):

    print("\n[EXECUTE SCRIPT NODE] Executing remediation script")

    # Example remediation result
    script_output = {
        "status": "success",
        "message": "Script executed successfully inside container"
    }

    print(script_output)

    state["tool_used"] += " + execute_script"
    state["result"] += " | " + str(script_output)

    return state


# ==========================================
# BUILD GRAPH
# ==========================================
builder = StateGraph(AlertState)


# ==========================================
# ADD NODES
# ==========================================
builder.add_node(
    "check_environment_access_node",
    check_environment_access_node
)

builder.add_node(
    "router_node",
    router_node
)

builder.add_node(
    "memory_node",
    memory_node
)

builder.add_node(
    "cpu_node",
    cpu_node
)

builder.add_node(
    "unknown_node",
    unknown_node
)

builder.add_node(
    "execute_script_node",
    execute_script_node
)


# ==========================================
# ENTRY POINT
# ==========================================
builder.set_entry_point("check_environment_access_node")


# ==========================================
# STEP 1:
# ACCESS CHECK
# ==========================================
builder.add_conditional_edges(
    "check_environment_access_node",
    access_router,
    {
        "failed": END,
        "router": "router_node"
    }
)


# ==========================================
# STEP 2:
# ISSUE ROUTING
# ==========================================
builder.add_conditional_edges(
    "router_node",
    issue_router,
    {
        "memory": "memory_node",
        "cpu": "cpu_node",
        "unknown": "unknown_node"
    }
)


# ==========================================
# TOOL → SCRIPT FLOW
# ==========================================
builder.add_edge(
    "memory_node",
    "execute_script_node"
)

builder.add_edge(
    "cpu_node",
    "execute_script_node"
)


# ==========================================
# END FLOWS
# ==========================================
builder.add_edge(
    "unknown_node",
    END
)

builder.add_edge(
    "execute_script_node",
    END
)


# ==========================================
# COMPILE GRAPH
# ==========================================
graph = builder.compile()


# ==========================================
# SAVE GRAPH IMAGE
# ==========================================
try:

    png_bytes = graph.get_graph().draw_mermaid_png()

    with open("Graph/graph.png", "wb") as f:
        f.write(png_bytes)

    print("\n✅ Graph saved successfully at Graph/graph.png")

except Exception as e:

    print(f"\n❌ Error saving graph: {e}")