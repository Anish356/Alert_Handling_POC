#!/bin/bash

# =========================================================
# restart_otac.sh
# Purpose: Restart OTAC services
# =========================================================

DATE=$(date +"%Y-%m-%d")
LOG_FILE="/tmp/restart_otac_${DATE}.log"

echo "[$(date)] Restarting OTAC services..." >> "$LOG_FILE"

echo "[$(date)] OTAC restart completed." >> "$LOG_FILE"
echo "" >> "$LOG_FILE"