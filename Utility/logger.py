import logging

from pathlib import Path
from datetime import datetime


# =========================================================
# BASE LOGGER
# =========================================================
def setup_logger(name: str = __name__) -> logging.Logger:

    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )

    # =====================================================
    # CONSOLE HANDLER
    # =====================================================
    console_handler = logging.StreamHandler()

    console_handler.setLevel(logging.INFO)

    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    logger.propagate = False

    return logger


# =========================================================
# CREATE API LOG FILE
# =========================================================
def attach_api_file_handler(
    logger: logging.Logger,
    host: str = "",
    customer: str = "",
    environment: str = ""
):

    # =====================================================
    # REMOVE OLD FILE HANDLERS
    # =====================================================
    for handler in logger.handlers[:]:

        if isinstance(handler, logging.FileHandler):
            logger.removeHandler(handler)
            handler.close()

    # =====================================================
    # LOG DIRECTORY
    # =====================================================
    log_dir = Path("logs")

    log_dir.mkdir(exist_ok=True)

    # =====================================================
    # TIMESTAMP
    # FORMAT:
    # 20260513_131427
    # =====================================================
    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")

    # =====================================================
    # IDENTIFIER
    # =====================================================
    if host and str(host).strip():

        identifier = (
            host
            .replace(".", "_")
            .replace("/", "_")
            .replace(" ", "_")
        )

    else:

        identifier = f"{customer}_{environment}"

        identifier = (
            identifier
            .replace(".", "_")
            .replace("/", "_")
            .replace(" ", "_")
        )

    # =====================================================
    # FINAL FILE NAME
    # Example:
    # 20260513_131427_gcp-ek3csw-sn86cs_cloud_eu.log
    # =====================================================
    filename = f"{timestamp}_{identifier}.log"

    log_file = log_dir / filename

    # =====================================================
    # FILE HANDLER
    # =====================================================
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )

    file_handler = logging.FileHandler(log_file)

    file_handler.setLevel(logging.INFO)

    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    logger.info(f"Log file created: {log_file}")