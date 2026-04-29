#!/bin/bash
# Archives log files older than N days. Keeps the logs directory clean.
# Usage: ./log_rotate.sh [days]  (default: 7)

DAYS=${1:-7}
LOG_DIR="../logs"
ARCHIVE_DIR="../logs/archive"

mkdir -p "$ARCHIVE_DIR"

echo "Archiving log files older than ${DAYS} days..."

COUNT=0
while IFS= read -r -d '' file; do
    FILENAME=$(basename "$file")
    gzip -c "$file" > "${ARCHIVE_DIR}/${FILENAME}.gz"
    rm "$file"
    echo "  Archived: ${FILENAME}"
    ((COUNT++))
done < <(find "$LOG_DIR" -maxdepth 1 -name "*.log" -mtime +"$DAYS" -print0)

echo "Done. Archived ${COUNT} file(s)."