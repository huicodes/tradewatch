#!/bin/bash
# Runs the full TradeWatch pipeline end-to-end.
# This is what you'd schedule with cron for daily operation.

set -e  # Exit on any error

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
PYTHON_DIR="${PROJECT_DIR}/python"
LOG_FILE="${PROJECT_DIR}/logs/pipeline_$(date +%Y%m%d_%H%M%S).log"

echo "========================================" | tee "$LOG_FILE"
echo "  TRADEWATCH PIPELINE RUN"              | tee -a "$LOG_FILE"
echo "  Started: $(date)"                      | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"

# Step 1: Health check
echo ""                                         | tee -a "$LOG_FILE"
echo "[STEP 1/5] Running health check..."       | tee -a "$LOG_FILE"
bash "${SCRIPT_DIR}/health_check.sh"            | tee -a "$LOG_FILE"

# Step 2: Generate simulated trades
echo ""                                         | tee -a "$LOG_FILE"
echo "[STEP 2/5] Generating today's trades..."  | tee -a "$LOG_FILE"
cd "$PYTHON_DIR"
python trade_generator.py --count 100           | tee -a "$LOG_FILE"

# Step 3: Generate simulated logs
echo ""                                         | tee -a "$LOG_FILE"
echo "[STEP 3/5] Generating application logs..."| tee -a "$LOG_FILE"
python log_generator.py --lines 500             | tee -a "$LOG_FILE"

# Step 4: Analyze logs
echo ""                                         | tee -a "$LOG_FILE"
echo "[STEP 4/5] Analyzing log files..."        | tee -a "$LOG_FILE"
python log_analyzer.py --all                    | tee -a "$LOG_FILE"

# Step 5: Generate trade report
echo ""                                         | tee -a "$LOG_FILE"
echo "[STEP 5/5] Generating trade report..."    | tee -a "$LOG_FILE"
python trade_reporter.py --days 1               | tee -a "$LOG_FILE"

echo ""                                         | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"
echo "  Pipeline complete: $(date)"             | tee -a "$LOG_FILE"
echo "  Full log: ${LOG_FILE}"                  | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"