-- sql/02_seed_data.sql
USE tradewatch;

-- Seed instruments
INSERT INTO instruments (symbol, company_name, sector) VALUES
('AAPL', 'Apple Inc.', 'Technology'),
('GOOGL', 'Alphabet Inc.', 'Technology'),
('JPM', 'JPMorgan Chase', 'Financial Services'),
('JNJ', 'Johnson & Johnson', 'Healthcare'),
('XOM', 'Exxon Mobil', 'Energy'),
('AMZN', 'Amazon.com Inc.', 'Technology'),
('BAC', 'Bank of America', 'Financial Services'),
('PFE', 'Pfizer Inc.', 'Healthcare'),
('TSLA', 'Tesla Inc.', 'Automotive'),
('WMT', 'Walmart Inc.', 'Retail');

-- Seed traders
INSERT INTO traders (first_name, last_name, desk, email) VALUES
('Alice', 'Chen', 'Equities', 'achen@example.com'),
('Bob', 'Martinez', 'Equities', 'bmartinez@example.com'),
('Carol', 'Williams', 'Derivatives', 'cwilliams@example.com'),
('David', 'Kim', 'Fixed Income', 'dkim@example.com'),
('Eva', 'Patel', 'Equities', 'epatel@example.com');