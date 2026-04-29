#!/bin/bash
# Checks if critical services are running and reports status.
# A production support analyst would run or schedule this regularly.

echo "========================================"
echo "  TRADEWATCH HEALTH CHECK"
echo "  $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================"

PASS=0
FAIL=0

# Check 1: Is MySQL running?
if systemctl is-active --quiet mysql 2>/dev/null || \
   mysqladmin ping -u root --silent 2>/dev/null; then
    echo "  [PASS] MySQL is running"
    ((PASS++))
else
    echo "  [FAIL] MySQL is NOT running"
    ((FAIL++))
fi

# Check 2: Can we connect to the tradewatch database?
if mysql -u root -e "USE tradewatch;" 2>/dev/null; then
    echo "  [PASS] tradewatch database is accessible"
    ((PASS++))
else
    echo "  [FAIL] tradewatch database is NOT accessible"
    ((FAIL++))
fi

# Check 3: Disk usage
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -lt 80 ]; then
    echo "  [PASS] Disk usage is ${DISK_USAGE}% (under 80% threshold)"
    ((PASS++))
else
    echo "  [WARN] Disk usage is ${DISK_USAGE}% (above 80% threshold)"
    ((FAIL++))
fi

# Check 4: Memory usage
MEM_AVAILABLE=$(free -m | awk 'NR==2 {printf "%.0f", ($7/$2)*100}')
if [ "$MEM_AVAILABLE" -gt 20 ]; then
    echo "  [PASS] Memory: ${MEM_AVAILABLE}% available"
    ((PASS++))
else
    echo "  [WARN] Memory: only ${MEM_AVAILABLE}% available"
    ((FAIL++))
fi

# Check 5: Are there any log files to process?
LOG_COUNT=$(find ../logs -name "*.log" -newer ../logs/.gitkeep 2>/dev/null | wc -l)
echo "  [INFO] ${LOG_COUNT} unprocessed log file(s) in logs/"

# Summary
echo "========================================"
echo "  Results: ${PASS} passed, ${FAIL} failed"
if [ "$FAIL" -gt 0 ]; then
    echo "  STATUS: ISSUES DETECTED — review above"
    exit 1
else
    echo "  STATUS: ALL CHECKS PASSED"
    exit 0
fi