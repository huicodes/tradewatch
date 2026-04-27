CREATE DATABASE IF NOT EXISTS tradewatch;
USE tradewatch;

-- Reference table for tradeable instruments
CREATE TABLE IF NOT EXISTS instruments (
    instrument_id INT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL UNIQUE,
    company_name VARCHAR(100) NOT NULL,
    sector VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Reference table for traders
CREATE TABLE IF NOT EXISTS traders (
    trader_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    desk VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Core trades table
CREATE TABLE IF NOT EXISTS trades (
    trade_id INT AUTO_INCREMENT PRIMARY KEY,
    trader_id INT NOT NULL,
    instrument_id INT NOT NULL,
    side ENUM('BUY', 'SELL') NOT NULL,
    quantity INT NOT NULL,
    price DECIMAL(12, 2) NOT NULL,
    total_value DECIMAL(15, 2) GENERATED ALWAYS AS (quantity * price) STORED,
    status ENUM('PENDING', 'EXECUTED', 'CANCELLED', 'FAILED') DEFAULT 'PENDING',
    trade_date DATE NOT NULL,
    trade_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (trader_id) REFERENCES traders(trader_id),
    FOREIGN KEY (instrument_id) REFERENCES instruments(instrument_id),
    INDEX idx_trade_date (trade_date),
    INDEX idx_status (status),
    INDEX idx_trader (trader_id)
);

-- Table for storing parsed log analysis results
CREATE TABLE IF NOT EXISTS log_events (
    event_id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    log_level ENUM('INFO', 'WARNING', 'ERROR', 'CRITICAL') NOT NULL,
    service VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    source_file VARCHAR(255),
    parsed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_log_level (log_level),
    INDEX idx_timestamp (timestamp)
);

-- Summary table for daily health reports
CREATE TABLE IF NOT EXISTS daily_summary (
    summary_id INT AUTO_INCREMENT PRIMARY KEY,
    report_date DATE NOT NULL UNIQUE,
    total_trades INT DEFAULT 0,
    total_volume DECIMAL(18, 2) DEFAULT 0,
    failed_trades INT DEFAULT 0,
    error_count INT DEFAULT 0,
    warning_count INT DEFAULT 0,
    critical_count INT DEFAULT 0,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);