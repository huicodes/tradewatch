-- sql/03_useful_queries.sql
USE tradewatch;

-- ============================================================
-- QUERY 1: Daily trade volume summary for today
-- Scenario: "How many trades did we process today?"
-- ============================================================
SELECT
    COUNT(*) AS total_trades,
    SUM(total_value) AS total_volume,
    SUM(CASE WHEN side = 'BUY' THEN 1 ELSE 0 END) AS buy_count,
    SUM(CASE WHEN side = 'SELL' THEN 1 ELSE 0 END) AS sell_count
FROM trades
WHERE trade_date = CURDATE();

-- ============================================================
-- QUERY 2: Top 5 traders by volume this week
-- Scenario: "Who are our most active traders?"
-- ============================================================
SELECT
    CONCAT(t.first_name, ' ', t.last_name) AS trader_name,
    t.desk,
    COUNT(tr.trade_id) AS trade_count,
    SUM(tr.total_value) AS total_volume
FROM traders t
INNER JOIN trades tr ON t.trader_id = tr.trader_id
WHERE tr.trade_date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
GROUP BY t.trader_id, t.first_name, t.last_name, t.desk
ORDER BY total_volume DESC
LIMIT 5;

-- ============================================================
-- QUERY 3: Failed trades with trader and instrument details
-- Scenario: "Show me all failed trades so I can investigate."
-- ============================================================
SELECT
    tr.trade_id,
    tr.trade_time,
    CONCAT(td.first_name, ' ', td.last_name) AS trader,
    i.symbol,
    tr.side,
    tr.quantity,
    tr.price,
    tr.total_value
FROM trades tr
INNER JOIN traders td ON tr.trader_id = td.trader_id
INNER JOIN instruments i ON tr.instrument_id = i.instrument_id
WHERE tr.status = 'FAILED'
ORDER BY tr.trade_time DESC;

-- ============================================================
-- QUERY 4: Volume by sector
-- Scenario: "How is trading distributed across sectors?"
-- ============================================================
SELECT
    i.sector,
    COUNT(tr.trade_id) AS trade_count,
    SUM(tr.total_value) AS sector_volume,
    ROUND(AVG(tr.price), 2) AS avg_price
FROM trades tr
INNER JOIN instruments i ON tr.instrument_id = i.instrument_id
GROUP BY i.sector
ORDER BY sector_volume DESC;

-- ============================================================
-- QUERY 5: Error frequency by hour (from parsed logs)
-- Scenario: "When do most errors occur? Is there a pattern?"
-- ============================================================
SELECT
    HOUR(timestamp) AS hour_of_day,
    COUNT(*) AS error_count
FROM log_events
WHERE log_level IN ('ERROR', 'CRITICAL')
GROUP BY HOUR(timestamp)
ORDER BY error_count DESC;

-- ============================================================
-- QUERY 6: Find duplicate trades (potential data quality issue)
-- Scenario: "Are there any duplicate entries we need to clean up?"
-- ============================================================
SELECT
    trader_id,
    instrument_id,
    side,
    quantity,
    price,
    trade_date,
    COUNT(*) AS duplicate_count
FROM trades
GROUP BY trader_id, instrument_id, side, quantity, price, trade_date
HAVING COUNT(*) > 1;

-- ============================================================
-- QUERY 7: Trades per instrument with status breakdown
-- Scenario: "Give me a status report for each ticker."
-- ============================================================
SELECT
    i.symbol,
    COUNT(*) AS total,
    SUM(CASE WHEN tr.status = 'EXECUTED' THEN 1 ELSE 0 END) AS executed,
    SUM(CASE WHEN tr.status = 'PENDING' THEN 1 ELSE 0 END) AS pending,
    SUM(CASE WHEN tr.status = 'FAILED' THEN 1 ELSE 0 END) AS failed,
    SUM(CASE WHEN tr.status = 'CANCELLED' THEN 1 ELSE 0 END) AS cancelled
FROM trades tr
INNER JOIN instruments i ON tr.instrument_id = i.instrument_id
GROUP BY i.symbol
ORDER BY total DESC;