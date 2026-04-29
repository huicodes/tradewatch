"""
Simulates incoming trades for the TradeWatch system.
Generates realistic trade data and inserts it into MySQL.

Usage:
    python trade_generator.py              # Generate 50 trades for today
    python trade_generator.py --count 200  # Generate 200 trades
    python trade_generator.py --days 7     # Generate trades across the past 7 days
"""

import random
import argparse
from datetime import datetime, timedelta
from db_config import get_connection, close_connection


# Realistic price ranges per instrument_id (keyed to seed data order)
PRICE_RANGES = {
    1: (170, 195),    # AAPL
    2: (140, 165),    # GOOGL
    3: (180, 210),    # JPM
    4: (150, 170),    # JNJ
    5: (100, 120),    # XOM
    6: (175, 200),    # AMZN
    7: (35, 45),      # BAC
    8: (25, 35),      # PFE
    9: (200, 280),    # TSLA
    10: (55, 70)     # WMT
}

STATUSES = ['EXECUTED', 'EXECUTED', 'EXECUTED', 'EXECUTED',
            'PENDING', 'CANCELLED', 'FAILED']
# Weighted so most trades succeed — realistic distribution


def generate_trades(count, days_back):
    """Generate and insert random trades into the database."""
    connection = get_connection()
    if not connection:
        print("[ERROR] Could not connect to database. Exiting.")
        return

    cursor = connection.cursor()
    trades_inserted = 0

    try:
        for _ in range(count):
            trader_id = random.randint(1, 5)
            instrument_id = random.randint(1, 10)
            side = random.choice(['BUY', 'SELL'])
            quantity = random.choice([10, 25, 50, 100, 200, 500, 1000])

            low, high = PRICE_RANGES[instrument_id]
            price = round(random.uniform(low, high), 2)

            status = random.choice(STATUSES)

            trade_date = datetime.now() - timedelta(
                days=random.randint(0, days_back)
            )
            trade_date_str = trade_date.strftime('%Y-%m-%d')

            query = """
                INSERT INTO trades
                    (trader_id, instrument_id, side, quantity, price,
                     status, trade_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            values = (trader_id, instrument_id, side, quantity,
                      price, status, trade_date_str)

            cursor.execute(query, values)
            trades_inserted += 1

        connection.commit()
        print(f"[SUCCESS] Inserted {trades_inserted} trades.")

    except Exception as e:
        connection.rollback()
        print(f"[ERROR] Failed to insert trades: {e}")

    finally:
        cursor.close()
        close_connection(connection)


def main():
    parser = argparse.ArgumentParser(
        description="Generate simulated trade data for TradeWatch"
    )
    parser.add_argument(
        '--count', type=int, default=50,
        help='Number of trades to generate (default: 50)'
    )
    parser.add_argument(
        '--days', type=int, default=0,
        help='Spread trades across this many past days (default: 0 = today only)'
    )
    args = parser.parse_args()

    print(f"Generating {args.count} trades across {args.days + 1} day(s)...")
    generate_trades(args.count, args.days)


if __name__ == "__main__":
    main()