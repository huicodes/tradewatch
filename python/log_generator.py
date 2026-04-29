"""
Simulates production application log output.
Creates realistic log files that the log analyzer will parse.

Usage:
    python log_generator.py                  # Generate 500 log lines
    python log_generator.py --lines 2000     # Generate 2000 log lines
"""

import random
import argparse
from datetime import datetime, timedelta


SERVICES = [
    'trade-engine', 'order-gateway', 'risk-service',
    'market-data-feed', 'settlement-service', 'auth-service'
]

LOG_TEMPLATES = {
    'INFO': [
        "Trade {trade_id} executed successfully for {symbol}",
        "Order received from trader {trader_id}: {side} {qty} {symbol}",
        "Market data update received for {symbol}: price={price}",
        "User {trader_id} authenticated successfully",
        "Health check passed for {service}",
        "Database connection pool: {pool_size} active connections",
        "Settlement completed for trade {trade_id}",
        "Risk check passed for order {trade_id}",
    ],
    'WARNING': [
        "High latency detected on {service}: {latency}ms",
        "Database connection pool nearing limit: {pool_size}/50",
        "Trade {trade_id} retry attempt {retry} of 3",
        "Market data delayed for {symbol} by {latency}ms",
        "Memory usage at {mem_pct}% on {service}",
        "Slow query detected on {service}: {latency}ms",
    ],
    'ERROR': [
        "Trade {trade_id} failed: insufficient margin for {symbol}",
        "Database connection timeout on {service} after {latency}ms",
        "Order validation failed for trader {trader_id}: invalid quantity",
        "Market data feed disconnected for {symbol}",
        "Risk limit exceeded for trader {trader_id}: exposure={exposure}",
        "Authentication failed for user {trader_id}: invalid credentials",
    ],
    'CRITICAL': [
        "SYSTEM: {service} is unresponsive — attempting restart",
        "SYSTEM: Database primary node failover initiated",
        "SYSTEM: Trade engine circuit breaker OPEN after {retry} failures",
        "SYSTEM: Disk space critical on /var/log: {mem_pct}% used",
    ],
}

# Weighted distribution — most entries should be INFO
LEVEL_WEIGHTS = {
    'INFO': 70,
    'WARNING': 18,
    'ERROR': 10,
    'CRITICAL': 2,
}

SYMBOLS = ['AAPL', 'GOOGL', 'JPM', 'JNJ', 'XOM',
           'AMZN', 'BAC', 'PFE', 'TSLA', 'WMT']


def generate_log_line(base_time):
    """Generate a single realistic log line."""
    level = random.choices(
        list(LEVEL_WEIGHTS.keys()),
        weights=list(LEVEL_WEIGHTS.values()),
        k=1
    )[0]

    template = random.choice(LOG_TEMPLATES[level])
    service = random.choice(SERVICES)

    message = template.format(
        trade_id=random.randint(10000, 99999),
        symbol=random.choice(SYMBOLS),
        trader_id=random.randint(1, 5),
        side=random.choice(['BUY', 'SELL']),
        qty=random.choice([10, 50, 100, 500, 1000]),
        price=round(random.uniform(25, 300), 2),
        service=service,
        latency=random.randint(100, 5000),
        pool_size=random.randint(30, 49),
        retry=random.randint(1, 3),
        mem_pct=random.randint(75, 99),
        exposure=random.randint(100000, 5000000),
    )

    # Advance time by a random small interval
    offset = timedelta(seconds=random.randint(1, 30))
    timestamp = (base_time + offset).strftime('%Y-%m-%d %H:%M:%S')

    return f"{timestamp} [{level}] [{service}] {message}\n", offset


def generate_log_file(line_count, output_path):
    """Generate a full log file."""
    current_time = datetime.now() - timedelta(hours=8)

    with open(output_path, 'w') as f:
        for _ in range(line_count):
            line, offset = generate_log_line(current_time)
            f.write(line)
            current_time += offset

    print(f"[SUCCESS] Generated {line_count} log lines in {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate simulated production logs"
    )
    parser.add_argument(
        '--lines', type=int, default=500,
        help='Number of log lines to generate (default: 500)'
    )
    args = parser.parse_args()

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_path = f"../logs/app_{timestamp}.log"

    generate_log_file(args.lines, output_path)


if __name__ == "__main__":
    main()