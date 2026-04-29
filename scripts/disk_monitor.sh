#!/bin/bash
# Monitors disk usage and alerts if any partition exceeds the threshold.

THRESHOLD=${1:-80}  # Default to 80%, can be overridden by argument

echo "Checking disk usage (threshold: ${THRESHOLD}%)..."
echo ""

ALERT=0

while read -r line; do
    USAGE=$(echo "$line" | awk '{print $5}' | sed 's/%//')
    MOUNT=$(echo "$line" | awk '{print $6}')
    FILESYSTEM=$(echo "$line" | awk '{print $1}')

    if [ "$USAGE" -ge "$THRESHOLD" ]; then
        echo "[ALERT] ${MOUNT} is at ${USAGE}% (${FILESYSTEM})"
        ALERT=1
    fi
done < <(df -h | grep '^/' )

if [ "$ALERT" -eq 0 ]; then
    echo "[OK] All partitions are under ${THRESHOLD}% usage."
fi