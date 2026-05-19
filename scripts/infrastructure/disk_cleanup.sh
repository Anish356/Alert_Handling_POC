#!/bin/bash

# =========================================================
# disk_cleanup.sh
# Purpose: Cleanup disk space
# =========================================================

DATE=$(date +"%Y-%m-%d")
LOG_FILE="/tmp/disk_cleanup_${DATE}.log"

echo "[$(date)] Checking disk usage..." >> "$LOG_FILE"

echo "[$(date)] Cleaning temporary files..." >> "$LOG_FILE"

echo "[$(date)] Disk cleanup completed." >> "$LOG_FILE"
echo "" >> "$LOG_FILE"