from pathlib import Path
from typing import List, Optional
from langchain.tools import tool
from Utility.logger import setup_logger

# =========================================================
# LOGGER
# =========================================================
logger = setup_logger("alert_workflow")

# =========================================================
# INFRASTRUCTURE DIAGNOSTIC AGENT
# =========================================================
@tool
def infrastructure_diagnostic_flow(scripts,host_name):

    """Perform infrastructure diagnostics"""

    logger.info("[INFRASTRUCTURE AGENT] Running diagnostics")

    output=docker_execution_agent(scripts=scripts,container_name=host_name)

    return output


# =========================================================
# SERVICE HEALTH AGENT
# =========================================================
@tool
def service_health_flow(scripts,host_name):

    """Perform service health diagnostics"""

    logger.info("[SERVICE HEALTH AGENT] Running checks")


    output=docker_execution_agent(scripts=scripts,container_name=host_name)

    return output


# =========================================================
# NETWORK DIAGNOSTICS AGENT
# =========================================================
@tool
def network_diagnostics_flow(scripts,host_name):

    """Perform network diagnostics"""

    logger.info("[NETWORK AGENT] Running diagnostics")


    output=docker_execution_agent(scripts=scripts,container_name=host_name)

    return output


# =========================================================
# APPLICATION DIAGNOSTICS AGENT
# =========================================================
@tool
def application_diagnostics_flow(scripts,host_name):

    """Perform application diagnostics"""

    logger.info("[APPLICATION AGENT] Running diagnostics")


    output=docker_execution_agent(scripts=scripts,container_name=host_name)

    return output


# =========================================================
# DOCKER EXECUTION AGENT
# =========================================================
def docker_execution_agent(scripts: dict, container_name: str ):

    """
    Execute multiple local shell scripts inside Docker container
    """

    import subprocess

    results = {}

    for script_no, (action, script_path) in enumerate(scripts.items(), start=1):

        logger.info(
            f"[EXECUTING SCRIPT] "
            f"ScriptNo={script_no} "
            f"Container={container_name} "
            f"Action={action} "
            f"Script={script_path}"
        )

        try:

            with open(script_path, "r", encoding="utf-8", newline=None) as file:
                script_content = file.read()

            script_content = script_content.replace("\r\n", "\n").replace("\r", "\n")

            result = subprocess.run(
                [
                    "docker",
                    "exec",
                    "-i",
                    container_name,
                    "sh",
                    "-s"
                ],
                input=script_content,
                capture_output=True,
                text=True
            )

            results[action] = {
                "script_no": script_no,
                "status": "success" if result.returncode == 0 else "failed",
                "container": container_name,
                "script": script_path,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }

            logger.info(
                f"[SCRIPT COMPLETED] "
                f"ScriptNo={script_no} "
                f"Action={action} "
                f"ExitCode={result.returncode}"
            )

        except Exception as e:

            logger.error(
                f"[EXECUTION FAILED] "
                f"ScriptNo={script_no} "
                f"Action={action} "
                f"Error={e}"
            )

            results[action] = {
                "script_no": script_no,
                "status": "failed",
                "container": container_name,
                "script": script_path,
                "error": str(e)
            }

    return results