"""
Generates trade analytics reports by querying MySQL.
Outputs a formatted summary to the terminal and saves to a file.

Usage:
    python trade_reporter.py             # Report for today
    python trade_reporter.py --days 7    # Report for the past 7 days
"""

import argparse
from datetime import datetime, timedelta
from db_config import get_connection, close_connection


def fetch_trade_summary(cursor, start_date, end_date):
    """Fetch overall trade statistics for the date range."""
    cursor.execute("""
        SELECT
            COUNT(*) AS total_trades,
            COALESCE(SUM(total_value), 0) AS total_volume,
            COALESCE(AVG(total_value), 0) AS avg_trade_value,
            SUM(CASE WHEN side = 'BUY' THEN 1 ELSE 0 END) AS buys,
            SUM(CASE WHEN side = 'SELL' THEN 1 ELSE 0 END) AS sells,
            SUM(CASE WHEN status = 'EXECUTED' THEN 1 ELSE 0 END) AS executed,
            SUM(CASE WHEN status = 'FAILED' THEN 1 ELSE 0 END) AS failed,
            SUM(CASE WHEN status = 'CANCELLED' THEN 1 ELSE 0 END) AS cancelled,
            SUM(CASE WHEN status = 'PENDING' THEN 1 ELSE 0 END) AS pending
        FROM trades
        WHERE trade_date BETWEEN %s AND %s
    """, (start_date, end_date))
    return cursor.fetchone()


def fetch_top_instruments(cursor, start_date, end_date, limit=5):
    """Fetch the most traded instruments by volume."""
    cursor.execute("""
        SELECT
            i.symbol,
            i.company_name,
            COUNT(t.trade_id) AS trade_count,
            SUM(t.total_value) AS volume
        FROM trades t
        INNER JOIN instruments i ON t.instrument_id = i.instrument_id
        WHERE t.trade_date BETWEEN %s AND %s
        GROUP BY i.instrument_id, i.symbol, i.company_name
        ORDER BY volume DESC
        LIMIT %s
    """, (start_date, end_date, limit))
    return cursor.fetchall()


def fetch_top_traders(cursor, start_date, end_date, limit=5):
    """Fetch the most active traders by volume."""
    cursor.execute("""
        SELECT
            CONCAT(td.first_name, ' ', td.last_name) AS name,
            td.desk,
            COUNT(t.trade_id) AS trade_count,
            SUM(t.total_value) AS volume
        FROM trades t
        INNER JOIN traders td ON t.trader_id = td.trader_id
        WHERE t.trade_date BETWEEN %s AND %s
        GROUP BY td.trader_id, td.first_name, td.last_name, td.desk
        ORDER BY volume DESC
        LIMIT %s
    """, (start_date, end_date, limit))
    return cursor.fetchall()


def fetch_sector_breakdown(cursor, start_date, end_date):
    """Fetch trading volume broken down by sector."""
    cursor.execute("""
        SELECT
            i.sector,
            COUNT(t.trade_id) AS trade_count,
            SUM(t.total_value) AS volume
        FROM trades t
        INNER JOIN instruments i ON t.instrument_id = i.instrument_id
        WHERE t.trade_date BETWEEN %s AND %s
        GROUP BY i.sector
        ORDER BY volume DESC
    """, (start_date, end_date))
    return cursor.fetchall()


def format_currency(value):
    """Format a number as currency."""
    return f"${value:,.2f}"


def generate_report(days_back):
    """Generate and print the full trade analytics report."""
    connection = get_connection()
    if not connection:
        print("[ERROR] Could not connect to database.")
        return

    cursor = connection.cursor()
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (
        datetime.now() - timedelta(days=days_back)
    ).strftime('%Y-%m-%d')

    try:
        summary = fetch_trade_summary(cursor, start_date, end_date)
        top_instruments = fetch_top_instruments(cursor, start_date, end_date)
        top_traders = fetch_top_traders(cursor, start_date, end_date)
        sectors = fetch_sector_breakdown(cursor, start_date, end_date)

        # Build report string
        report_lines = []
        report_lines.append("=" * 65)
        report_lines.append("  TRADEWATCH — TRADE ANALYTICS REPORT")
        report_lines.append(f"  Period: {start_date} to {end_date}")
        report_lines.append(
            f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        report_lines.append("=" * 65)

        if summary:
            total, volume, avg_val, buys, sells, ex, fail, canc, pend = summary
            report_lines.append(f"\n  OVERVIEW")
            report_lines.append(f"  {'Total trades':<25} {total:>10,}")
            report_lines.append(
                f"  {'Total volume':<25} {format_currency(volume):>18}"
            )
            report_lines.append(
                f"  {'Avg trade value':<25} {format_currency(avg_val):>18}"
            )
            report_lines.append(f"  {'Buys / Sells':<25} {buys:>5,} / {sells:>5,}")
            report_lines.append(f"\n  STATUS BREAKDOWN")
            report_lines.append(f"  {'Executed':<25} {ex:>10,}")
            report_lines.append(f"  {'Pending':<25} {pend:>10,}")
            report_lines.append(f"  {'Cancelled':<25} {canc:>10,}")
            report_lines.append(f"  {'Failed':<25} {fail:>10,}")
            if total > 0:
                fail_rate = (fail / total) * 100
                report_lines.append(
                    f"  {'Failure rate':<25} {fail_rate:>9.1f}%"
                )

        report_lines.append(f"\n  TOP INSTRUMENTS BY VOLUME")
        report_lines.append(f"  {'Symbol':<8} {'Company':<25} "
                            f"{'Trades':>7} {'Volume':>18}")
        report_lines.append("  " + "-" * 60)
        for symbol, company, count, vol in top_instruments:
            report_lines.append(
                f"  {symbol:<8} {company:<25} {count:>7,} "
                f"{format_currency(vol):>18}"
            )

        report_lines.append(f"\n  TOP TRADERS BY VOLUME")
        report_lines.append(f"  {'Trader':<20} {'Desk':<15} "
                            f"{'Trades':>7} {'Volume':>18}")
        report_lines.append("  " + "-" * 60)
        for name, desk, count, vol in top_traders:
            report_lines.append(
                f"  {name:<20} {desk:<15} {count:>7,} "
                f"{format_currency(vol):>18}"
            )

        report_lines.append(f"\n  SECTOR BREAKDOWN")
        report_lines.append(f"  {'Sector':<25} {'Trades':>7} {'Volume':>18}")
        report_lines.append("  " + "-" * 50)
        for sector, count, vol in sectors:
            report_lines.append(
                f"  {sector:<25} {count:>7,} {format_currency(vol):>18}"
            )

        report_lines.append("\n" + "=" * 65)

        # Print to terminal
        report_text = "\n".join(report_lines)
        print(report_text)

        # Save to file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = f"../reports/trade_report_{timestamp}.txt"
        with open(report_path, 'w') as f:
            f.write(report_text)
        print(f"\n  Report saved to {report_path}")

    except Exception as e:
        print(f"[ERROR] Report generation failed: {e}")

    finally:
        cursor.close()
        close_connection(connection)


def main():
    parser = argparse.ArgumentParser(
        description="Generate trade analytics report from TradeWatch database"
    )
    parser.add_argument(
        '--days', type=int, default=0,
        help='Number of days to look back (default: 0 = today only)'
    )
    args = parser.parse_args()

    generate_report(args.days)


if __name__ == "__main__":
    main()