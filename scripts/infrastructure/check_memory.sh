#!/bin/sh

DATE=$(date +"%Y-%m-%d")
LOG_FILE="/tmp/check_memory_${DATE}.log"

echo "[$(date)] Checking memory utilization..." >> "$LOG_FILE"

echo "[$(date)] ===== FREE MEMORY =====" >> "$LOG_FILE"

free -h >> "$LOG_FILE"

echo "[$(date)] ===== TOP MEMORY PROCESSES =====" >> "$LOG_FILE"

ps -eo pid,ppid,cmd,%mem,%cpu --sort=-%mem | head >> "$LOG_FILE"

echo "[$(date)] Memory check completed." >> "$LOG_FILE"
echo "" >> "$LOG_FILE"