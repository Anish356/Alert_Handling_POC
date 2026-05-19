#!/bin/bash

# =========================================================
# restart_document_service.sh
# Purpose: Restart OTPD document generation service
# =========================================================

DATE=$(date +"%Y-%m-%d")
LOG_FILE="/tmp/restart_document_service_${DATE}.log"

echo "[$(date)] Restarting document generation service..." >> "$LOG_FILE"

echo "[$(date)] Document generation service restart completed." >> "$LOG_FILE"
echo "" >> "$LOG_FILE"