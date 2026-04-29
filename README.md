# TradeWatch

A production support monitoring system and trade analytics pipeline built
with Python, MySQL, Bash, and Linux — simulating the kind of tooling used
in financial services technology teams.

## What This Project Does

TradeWatch simulates a trading environment where:

1. **Trades are generated** with realistic instruments, traders, prices,
   and statuses (including failures and cancellations).
2. **Application logs are produced** mimicking multiple microservices
   (trade engine, order gateway, risk service, etc.).
3. **Logs are parsed and analyzed** using Python with regex, then
   stored in MySQL for querying.
4. **Trade analytics reports** are generated from the database showing
   volume, top traders, sector breakdowns, and failure rates.
5. **Shell scripts automate monitoring** — health checks, disk monitoring,
   log rotation, and full pipeline orchestration.
6. **Cron schedules** run everything on a production-like cadence.

## Tech Stack

| Category     | Technology                                                                                |
|--------------|-------------------------------------------------------------------------------------------|
| Language     | Python 3, Bash                                                                            |
| Database     | MySQL                                                                                     |
| OS           | Linux (Ubuntu)                                                                            |
| Automation   | cron, shell scripts                                                                       |
| Version Ctrl | Git                                                                                       |
| Concepts     | CRUD, log parsing, regex, production monitoring, ITIL-style health checks, data pipelines |


## Project Structure

(paste the directory tree from the top of this guide)

## Setup & Installation

1. Clone the repository:
   ```
   git clone https://github.com/huicodes/tradewatch.git
   cd tradewatch
   ```

2. Set up MySQL:
   ```
   mysql -u your_usrnm -p < sql/01_create_database.sql
   mysql -u your_usrnm -p < sql/02_seed_data.sql
   ```

3. Install Python dependencies:
   ```
   pip install mysql-connector-python
   ```

4. Update database credentials in `python/db_config.py`.

5. Run the full pipeline:
   ```
   bash scripts/run_pipeline.sh
   ```

## Configuration

This project uses environment variables for database credentials. To set up:

1. Copy the example file:
   ```
   cp .env.example .env
   ```
   
2. Edit `.env` and fill in your actual MySQL credentials. 
    
3. The application will automatically load these values at startup.

## Sample Output

(paste a snippet of your trade report and log analysis output here)

## Skills Demonstrated

- **Linux:** File system navigation, permissions, process management,
  piping, grep, find, system monitoring (df, free, top)
- **SQL/MySQL:** Schema design, CRUD operations, JOINs, aggregations,
  GROUP BY/HAVING, indexes, transactions
- **Python:** Functions, file I/O, regex, CSV processing, argparse,
  error handling, database connectivity, data structures
- **DevOps:** Shell scripting, cron scheduling, log rotation, health
  checks, pipeline automation, monitoring
- **Domain:** Financial trading concepts (instruments, traders, order
  sides, trade statuses, sector analysis)