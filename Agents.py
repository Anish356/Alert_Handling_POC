from langchain.tools import tool
import subprocess


# ==========================================
# COMMON DOCKER EXECUTOR
# ==========================================
def run_docker_command(container_name: str, command: list):
    """
    Generic Docker command runner
    """

    if not container_name:
        return {
            "status": "failed",
            "error": "container_name is required"
        }

    full_command = ["docker", "exec", container_name] + command

    print(f"\n[DOCKER EXEC] Running: {' '.join(full_command)}")

    try:

        result = subprocess.run(
            full_command,
            capture_output=True,
            text=True,
            timeout=10
        )

        # Command failed
        if result.returncode != 0:

            return {
                "container": container_name,
                "status": "failed",
                "error": result.stderr.strip()
            }

        # Command success
        return {
            "container": container_name,
            "status": "success",
            "output": result.stdout.strip()
        }

    except subprocess.TimeoutExpired:

        return {
            "container": container_name,
            "status": "failed",
            "error": "Command timed out"
        }

    except Exception as e:

        return {
            "container": container_name,
            "status": "failed",
            "error": str(e)
        }


# ==========================================
# MEMORY TOOL
# ==========================================
@tool
def memory_check(container_name: str):
    """
    Check memory usage inside Docker container
    """

    return run_docker_command(
        container_name,
        ["free", "-h"]
    )


# ==========================================
# CPU TOOL
# ==========================================
@tool
def cpu_check(container_name: str):
    """
    Check CPU usage inside Docker container
    """

    return run_docker_command(
        container_name,
        ["top", "-b", "-n", "1"]
    )


# ==========================================
# ENTER CONTAINER TOOL
# ==========================================
@tool
def enter_container(container_name: str):
    """
    Verify Docker container access using whoami
    """

    result = run_docker_command(
        container_name,
        ["whoami"]
    )

    # Customize response
    if result["status"] == "success":

        return {
            "container": container_name,
            "user": result["output"],
            "status": "connected"
        }

    return {
        "container": container_name,
        "status": "failed",
        "error": result["error"]
    }


# ==========================================
# DISK TOOL (OPTIONAL)
# ==========================================
@tool
def disk_check(container_name: str):
    """
    Check disk usage inside Docker container
    """

    return run_docker_command(
        container_name,
        ["df", "-h"]
    )


# ==========================================
# PROCESS TOOL (OPTIONAL)
# ==========================================
@tool
def process_check(container_name: str):
    """
    Check running processes inside Docker container
    """

    return run_docker_command(
        container_name,
        ["ps", "-ef"]
    )