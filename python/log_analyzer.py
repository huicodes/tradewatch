"""
Parses production log files, extracts insights, and stores results in MySQL.
This is the core tool a production support analyst would use.

Usage:
    python log_analyzer.py ../logs/app_20250101_120000.log
    python log_analyzer.py --all    # Analyze all log files in ../logs/
"""

import re
import os
import argparse
from datetime import datetime
from collections import Counter
from db_config import get_connection, close_connection


# Regex pattern matching the log format from log_generator.py
LOG_PATTERN = re.compile(
    r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) '
    r'\[(INFO|WARNING|ERROR|CRITICAL)\] '
    r'\[([^\]]+)\] '
    r'(.+)$'
)


def parse_log_file(filepath):
    """
    Parse a log file and return structured data.
    Returns a list of dicts, one per log line.
    """
    events = []
    unparsed_count = 0

    with open(filepath, 'r') as f:
        for line_number, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue

            match = LOG_PATTERN.match(line)
            if match:
                events.append({
                    'timestamp': match.group(1),
                    'level': match.group(2),
                    'service': match.group(3),
                    'message': match.group(4),
                    'source_file': os.path.basename(filepath),
                })
            else:
                unparsed_count += 1

    print(f"  Parsed {len(events)} events "
          f"({unparsed_count} lines could not be parsed)")
    return events


def analyze_events(events):
    """Produce a summary analysis of parsed log events."""
    if not events:
        print("  No events to analyze.")
        return {}

    level_counts = Counter(e['level'] for e in events)
    service_errors = Counter(
        e['service'] for e in events
        if e['level'] in ('ERROR', 'CRITICAL')
    )

    # Find time range
    timestamps = [e['timestamp'] for e in events]
    first = min(timestamps)
    last = max(timestamps)

    summary = {
        'total_events': len(events),
        'info_count': level_counts.get('INFO', 0),
        'warning_count': level_counts.get('WARNING', 0),
        'error_count': level_counts.get('ERROR', 0),
        'critical_count': level_counts.get('CRITICAL', 0),
        'time_range': f"{first} to {last}",
        'top_error_services': service_errors.most_common(5),
    }

    return summary


def print_report(summary, filepath):
    """Print a formatted analysis report to the terminal."""
    print("\n" + "=" * 60)
    print(f"  LOG ANALYSIS REPORT")
    print(f"  File: {os.path.basename(filepath)}")
    print("=" * 60)
    print(f"  Time range   : {summary.get('time_range', 'N/A')}")
    print(f"  Total events : {summary.get('total_events', 0)}")
    print("-" * 60)
    print(f"  INFO          : {summary.get('info_count', 0)}")
    print(f"  WARNING       : {summary.get('warning_count', 0)}")
    print(f"  ERROR         : {summary.get('error_count', 0)}")
    print(f"  CRITICAL      : {summary.get('critical_count', 0)}")
    print("-" * 60)

    top_services = summary.get('top_error_services', [])
    if top_services:
        print("  Top services with errors/criticals:")
        for service, count in top_services:
            bar = "#" * min(count, 40)
            print(f"    {service:25s} {count:4d}  {bar}")

    print("=" * 60 + "\n")


def store_events_in_db(events):
    """Insert parsed events into the log_events table."""
    connection = get_connection()
    if not connection:
        print("[ERROR] Could not connect to database.")
        return 0

    cursor = connection.cursor()
    inserted = 0

    try:
        query = """
            INSERT INTO log_events
                (timestamp, log_level, service, message, source_file)
            VALUES (%s, %s, %s, %s, %s)
        """
        for event in events:
            cursor.execute(query, (
                event['timestamp'],
                event['level'],
                event['service'],
                event['message'],
                event['source_file'],
            ))
            inserted += 1

        connection.commit()
        print(f"  Stored {inserted} events in database.")

    except Exception as e:
        connection.rollback()
        print(f"[ERROR] Failed to store events: {e}")

    finally:
        cursor.close()
        close_connection(connection)

    return inserted


def save_report_to_file(summary, filepath):
    """Save the analysis report as a text file in the reports directory."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = f"../reports/log_report_{timestamp}.txt"

    with open(report_path, 'w') as f:
        f.write(f"Log Analysis Report\n")
        f.write(f"Source: {os.path.basename(filepath)}\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"{'=' * 50}\n\n")
        for key, value in summary.items():
            f.write(f"{key}: {value}\n")

    print(f"  Report saved to {report_path}")


def process_file(filepath):
    """Full pipeline for a single log file."""
    print(f"\nProcessing: {filepath}")
    events = parse_log_file(filepath)
    summary = analyze_events(events)

    if summary:
        print_report(summary, filepath)
        store_events_in_db(events)
        save_report_to_file(summary, filepath)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze production log files and store results in MySQL"
    )
    parser.add_argument(
        'logfile', nargs='?', default=None,
        help='Path to a specific log file to analyze'
    )
    parser.add_argument(
        '--all', action='store_true',
        help='Analyze all .log files in the ../logs/ directory'
    )
    args = parser.parse_args()

    if args.all:
        log_dir = "../logs"
        log_files = sorted([
            os.path.join(log_dir, f)
            for f in os.listdir(log_dir) if f.endswith('.log')
        ])
        if not log_files:
            print("No log files found in ../logs/")
            return
        print(f"Found {len(log_files)} log file(s) to analyze.")
        for lf in log_files:
            process_file(lf)

    elif args.logfile:
        if not os.path.exists(args.logfile):
            print(f"[ERROR] File not found: {args.logfile}")
            return
        process_file(args.logfile)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()