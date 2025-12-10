import sqlite3
import os
from pathlib import Path
from sources.logger import Logger

logger = Logger("database.log")

# Database file path
DB_PATH = Path(__file__).parent.parent / "las.db"

def get_connection():
    """Get a database connection."""
    return sqlite3.connect(str(DB_PATH))

def initialize_database():
    """
    Initialize the database with required tables.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Create user_preferences table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Set default preferences if they don't exist
        defaults = [
            ('selected_provider', 'ollama'),
            ('selected_model', 'tinydolphin'),
            ('ollama_base_url', 'http://localhost:11434'),
        ]
        
        for key, value in defaults:
            cursor.execute('''
                INSERT OR IGNORE INTO user_preferences (key, value)
                VALUES (?, ?)
            ''', (key, value))
        
        conn.commit()
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise
    finally:
        conn.close()

def get_preference(key: str) -> str | None:
    """Get a preference value by key."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT value FROM user_preferences WHERE key = ?', (key,))
        result = cursor.fetchone()
        return result[0] if result else None
    finally:
        conn.close()

def set_preference(key: str, value: str):
    """Set or update a preference value."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO user_preferences (key, value, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(key) DO UPDATE SET
                value = excluded.value,
                updated_at = CURRENT_TIMESTAMP
        ''', (key, value))
        conn.commit()
        logger.info(f"Preference set: {key} = {value}")
    finally:
        conn.close()

def get_all_preferences() -> dict:
    """Get all preferences as a dict."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT key, value FROM user_preferences')
        return {row[0]: row[1] for row in cursor.fetchall()}
    finally:
        conn.close()

# Initialize on module import
if not DB_PATH.exists():
    logger.info("Database file not found, creating new database")
    initialize_database()
