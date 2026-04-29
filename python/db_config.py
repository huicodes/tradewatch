"""
Database connection configuration for TradeWatch.
Centralizes connection settings so they're not repeated in every script.
"""

import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv


# Load variables from .env file in the project root.
# This walks up the directory tree until it finds a .env file.
load_dotenv()


DB_CONFIG = {
    "host": os.getenv("TRADEWATCH_DB_HOST", "localhost"),
    "user": os.getenv("TRADEWATCH_DB_USER", "tradewatch_user"),
    "password": os.getenv("TRADEWATCH_DB_PASSWORD", ""),
    "database": os.getenv("TRADEWATCH_DB_NAME", "tradewatch")
}


def get_connection():
    """Create and return a database connection."""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"[ERROR] Failed to connect to MySQL: {e}")
        return None


def close_connection(connection):
    """Safely close a database connection."""
    if connection and connection.is_connected():
        connection.close()