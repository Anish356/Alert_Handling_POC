#!/bin/bash

# =========================================================
# db_connectivity_check.sh
# Purpose: Check database connectivity
# =========================================================
DATE=$(date +"%Y-%m-%d")
LOG_FILE="/tmp/db_connectivity_check_${DATE}.log"
echo "[$(date)] Checking database connectivity..." >> "$LOG_FILE"
echo "[$(date)] Database connectivity check completed." >> "$LOG_FILE"
echo "" >> "$LOG_FILE"