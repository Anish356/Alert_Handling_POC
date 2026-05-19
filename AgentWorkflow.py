import json
import traceback
import Agents
from pathlib import Path
from datetime import datetime
from typing import TypedDict, Optional, List, Dict, Any

from langgraph.graph import StateGraph, END

from Utility.logger import setup_logger, attach_api_file_handler


# =========================================================
# LOGGER
# =========================================================
logger = setup_logger("alert_workflow")
logger.info("[WORKFLOW INIT] Logger initialized")


# =========================================================
# AUTO LOAD AGENTS
# =========================================================
AVAILABLE_AGENTS = {
    getattr(Agents, name).name: getattr(Agents, name)
    for name in dir(Agents)
    if hasattr(getattr(Agents, name), "invoke")
}



logger.info(f"[AGENTS LOADED] Count={len(AVAILABLE_AGENTS)}")


# =========================================================
# NORMALIZATION
# =========================================================
def normalize_input(payload: dict) -> dict:
    logger.info("[NORMALIZE INPUT] Start")

    normalized = {
        "data": payload.get("data", {}),
        "agent_route": payload.get("agent_route", "")
                        or payload.get("data", {}).get("agent_route", ""),
        "error": payload.get("error"),
        "warnings": payload.get("warnings", []),
        "access_verified": payload.get("access_verified", False),
        "remediation_status": payload.get("remediation_status", ""),
        "execution_log": []
    }

    logger.info(f"[NORMALIZE INPUT] Done | keys={list(normalized.keys())}")
    return normalized


# =========================================================
# STATE
# =========================================================
class AlertState(TypedDict, total=False):

    # Raw Payload
    data: Dict[str, Any]

    # Extracted Important Fields
    customer_name: str
    host:str
    env: str
    selected_agent: str
    alert_code: str

    # Routing
    agent_route: str
    matched_action: Dict[str, Any]

    # Verification
    access_verified: bool
    env_login: bool


    # Execution
    agent_output: Dict[str, Any]
    scripts_to_execute: Dict[str, str]
    script_execution_results: Dict[str, Any]

    # Workflow Status
    remediation_status: str
    error: Optional[str]
    warnings: List[str]

    # Logs
    execution_log: List[Dict[str, Any]]


# =========================================================
# WORKFLOW
# =========================================================
class AlertWorkflow:

    def __init__(self):
        logger.info("[WORKFLOW] Initializing")

        self.builder = StateGraph(AlertState)

        self._add_nodes()
        self._add_dynamic_agent_nodes()
        self._add_edges()

        self.graph = self.builder.compile()

        logger.info("[WORKFLOW] Compiled successfully")


    # =====================================================
    def prepare_input(self, input_state: dict) -> dict:
        logger.info("[PREPARE INPUT] invoked")
        return normalize_input(input_state)


    # =====================================================
    def log_step(self, state, node, status, output=None, error=None, input_data=None):

        state.setdefault("execution_log", [])

        log_entry = {
            "node": node,
            "status": status,
            "timestamp": datetime.utcnow().isoformat(),
            "input": input_data,
            "output": output,
            "error": str(error) if error else None,
            "trace": traceback.format_exc() if error else None
        }

        state["execution_log"].append(log_entry)
        #logger.info(f"[LOG STEP] node={node} status={status}")


    # =====================================================
    def route_model(self, state):
        logger.info("[NODE] route_model triggered")
        return state


    # =====================================================
    def fetch_environment_details_node(self, state):

        logger.info("[NODE] fetch_environment_details_node START")

        try:
            data = state.get("data", {})

            customer_name = (data.get("customer") or "").strip().lower()
            incoming_host = data.get("host")
            incoming_env = data.get("environment")

            logger.info(f"[ENV SEARCH] customer={customer_name} env={incoming_env} host={incoming_host}")

            with open("config/env_config.json", "r") as f:
                env_data = json.load(f)

            matched_env = next(
                (
                    item for item in env_data
                    if (item.get("customer_name") or "").lower() == customer_name
                ),
                None
            )

            if matched_env:

                logger.info(f"[ENV MATCH FOUND] {matched_env}")

                state["customer_name"] = matched_env.get("customer_name")
                state["host"] = incoming_host or matched_env.get("host")
                state["env"] = incoming_env or matched_env.get("env")

                state["environment_details"] = matched_env
                state["access_verified"] = True

            else:

                logger.warning(f"[ENV NOT FOUND] customer={customer_name}")

                state["access_verified"] = False
                state["environment_details"] = {}

            self.log_step(
                state,
                "fetch_environment_details_node",
                "success",
                output={
                    "customer_name": state.get("customer_name"),
                    "host": state.get("host"),
                    "env": state.get("env")
                }
            )

        except Exception as e:

            logger.error(f"[ENV ERROR] {e}")

            state["access_verified"] = False
            state["environment_details"] = {}

            self.log_step(
                state,
                "fetch_environment_details_node",
                "failed",
                error=e
            )

        logger.info("[NODE] fetch_environment_details_node END")

        return state


    # =====================================================
    def access_router(self, state):
        result = "continue" if state.get("access_verified") else "failed"
        logger.info(f"[ACCESS ROUTER] {result}")
        return result


    # =====================================================
    def identify_alert_action_node(self, state):

        logger.info("[NODE] identify_alert_action_node START")

        try:

            data = state.get("data", {})

            selected_agent = (
                data.get("selected_agent")
                or state.get("agent_route")
                or state.get("selected_agent")
            ).replace("_agent", "_flow")

            logger.info(f"[SELECTED AGENT] {selected_agent}")

            with open("config/alert_action_cfg.json", "r") as f:
                config_data = json.load(f)

            matched_actions = [
                item for item in config_data
                if item.get("agent") == selected_agent
            ]

            if matched_actions:

                scripts_to_execute = {
                    item.get("action"): item.get("script_path")
                    for item in matched_actions
                }

                logger.info(f"[MATCH FOUND] scripts={scripts_to_execute}")

                state["selected_agent"] = selected_agent
                state["matched_action"] = matched_actions
                state["scripts_to_execute"] = scripts_to_execute
                state["remediation_status"] = "action_matched"

            else:

                logger.warning(f"[NO MATCH] agent={selected_agent}")

                state["selected_agent"] = selected_agent
                state["matched_action"] = []
                state["scripts_to_execute"] = {}
                state["remediation_status"] = "unknown"

            self.log_step(
                state,
                "identify_alert_action_node",
                state["remediation_status"],
                output={
                    "selected_agent": selected_agent,
                    "scripts_to_execute": state.get("scripts_to_execute")
                }
            )

        except Exception as e:

            logger.error(f"[ACTION NODE ERROR] {e}")

            state["remediation_status"] = "failed"

            self.log_step(
                state,
                "identify_alert_action_node",
                "failed",
                error=e
            )

        logger.info("[NODE] identify_alert_action_node END")

        return state


    # =====================================================
    def agent_router(self, state):

        selected_agent = state.get("selected_agent") or ""

        result = (
            selected_agent
            if selected_agent in AVAILABLE_AGENTS
            else "unsupported_alert"
        )

        logger.info(f"[AGENT ROUTER] {result}")

        return result


    # =====================================================
    def create_agent_node(self, agent_name):

        def node(state):
        
            return state

        return node


    # =====================================================
    def login_node(self, state):

        logger.info("[NODE] login_node START")

        import subprocess

        try:

            host_name = state.get("host")

            if not host_name:
                raise Exception("Host name missing")

            result = subprocess.run(
                ["docker", "exec", host_name, "echo", "CONNECTED"],
                capture_output=True,
                text=True
            )

            state["env_login"] = result.returncode == 0

            logger.info(
                f"[LOGIN STATUS] Host={host_name} "
                f"Success={state['env_login']}"
            )

            self.log_step(
                state,
                "login_node",
                "success" if state["env_login"] else "failed",
                output=result.stdout,
                error=result.stderr if result.returncode != 0 else None
            )

        except Exception as e:

            state["env_login"] = False

            logger.error(f"[LOGIN ERROR] {e}")

            self.log_step(
                state,
                "login_node",
                "failed",
                error=e
            )

        logger.info("[NODE] login_node END")

        return state


    # =====================================================
    def script_executed_node(self, state):

        logger.info("[NODE] script_executed_node START")

        try:

            selected_agent = state.get("selected_agent")

            #logger.info(f"[AGENT SELECTED] {selected_agent}")

            if selected_agent not in AVAILABLE_AGENTS:
                raise Exception(f"Agent not found: {selected_agent}")

            agent = AVAILABLE_AGENTS[selected_agent]

            scripts_to_execute = state.get("scripts_to_execute", {})

            logger.info(f"[SCRIPTS TO EXECUTE] {scripts_to_execute}")

            host_name = state.get("host")

            output = agent.invoke({
                "scripts": scripts_to_execute,
                "host_name": host_name
            })

            logger.info(f"[AGENT OUTPUT] {output}")

            state["agent_output"] = output
            state["script_execution_results"] = output
            state["remediation_status"] = "completed"

            self.log_step(
                state,
                "script_executed_node",
                "success",
                output=output
            )

        except Exception as e:

            logger.error(f"[SCRIPT EXECUTION ERROR] {e}")

            state["remediation_status"] = "failed"

            self.log_step(
                state,
                "script_executed_node",
                "failed",
                error=e
            )

        logger.info("[NODE] script_executed_node END")

        return state


    # =====================================================
    def unsupported_alert(self, state):
        logger.warning("[UNKNOWN NODE]")
        return state


    # =====================================================
    def _add_nodes(self):
        self.builder.add_node("route_model", self.route_model)
        self.builder.add_node("fetch_environment_details_node", self.fetch_environment_details_node)
        self.builder.add_node("identify_alert_action_node", self.identify_alert_action_node)
        self.builder.add_node("login_node", self.login_node)
        self.builder.add_node("script_executed_node", self.script_executed_node)
        self.builder.add_node("unsupported_alert", self.unsupported_alert)


    # =====================================================
    def _add_dynamic_agent_nodes(self):

        for name in AVAILABLE_AGENTS:
            #name = name.replace("agent", "flow")
            self.builder.add_node(name, self.create_agent_node(name))


    # =====================================================
    def _add_edges(self):

        self.builder.set_entry_point("route_model")

        self.builder.add_edge("route_model", "fetch_environment_details_node")

        self.builder.add_conditional_edges(
            "fetch_environment_details_node",
            self.access_router,
            {"continue": "identify_alert_action_node", "failed": END}
        )

        self.builder.add_conditional_edges(
            "identify_alert_action_node",
            self.agent_router,
            {name: name for name in AVAILABLE_AGENTS} | {"unsupported_alert": "unsupported_alert"}
        )

        for name in AVAILABLE_AGENTS:
            #name = name.replace("agent", "flow")
            self.builder.add_edge(name, "login_node")

        self.builder.add_edge("login_node", "script_executed_node")
        self.builder.add_edge("script_executed_node", END)
        self.builder.add_edge("unsupported_alert", END)


    # =====================================================
    def save_graph(self):
        png_bytes = self.graph.get_graph().draw_mermaid_png()

        graph_dir = Path("Graph")
        graph_dir.mkdir(exist_ok=True)

        graph_path = graph_dir / "graph.png"

        with open(graph_path, "wb") as f:
            f.write(png_bytes)

        logger.info(f"[GRAPH SAVED] {graph_path}")


    # =====================================================
    def run(self, input_state):

        logger.info("[RUN] Workflow started")

        data = input_state.get("data") or {}

        attach_api_file_handler(
            logger=logger,
            host=data.get("host", ""),
            customer=data.get("customer", ""),
            environment=data.get("environment", "")
        )

        clean = self.prepare_input(input_state)

        logger.info("[RUN] invoking graph")
        return self.graph.invoke(clean)


# =========================================================
# INIT
# =========================================================
workflow = AlertWorkflow()
workflow.save_graph()
graph = workflow.graph


# =========================================================
# TEST
# =========================================================
if __name__ == "__main__":

    sample_input = {
        "success": True,
        "data": {
            "customer": "EK",
            "source": "New Relic",
            "service": "Kubernetes",
            "alert_code": "CXE701-0200",
            "environment": None,
            "host": None,
            "issue": "k8s Volume is almost full",
            "alert_type": "Type6",
            "severity": "critical"
        },
        "agent_route": "Type6_critical_escalation_agent",
        "error": None,
        "warnings": []
    }

    result = workflow.run(sample_input)

    print("\nFINAL RESULT:\n")
    print(json.dumps(result, indent=4))