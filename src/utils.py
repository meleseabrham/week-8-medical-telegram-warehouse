import logging
import os
import psycopg2
from typing import Optional
from .config import DBConfig, DEFAULT_LOG_FORMAT

def setup_logging(log_filename: str, log_level: int = logging.INFO) -> None:
    """Sets up logging with a consistent format."""
    os.makedirs('logs', exist_ok=True)
    logging.basicConfig(
        filename=os.path.join('logs', log_filename),
        level=log_level,
        format=DEFAULT_LOG_FORMAT,
        force=True # Ensure it overrides any previous config
    )
    # Also add console logging
    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter(DEFAULT_LOG_FORMAT))
    logging.getLogger('').addHandler(console)

def get_db_connection(config: DBConfig) -> Optional[psycopg2.extensions.connection]:
    """Establishes a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            host=config.host,
            port=config.port,
            database=config.name,
            user=config.user,
            password=config.password
        )
        return conn
    except Exception as e:
        logging.error(f"Error connecting to database: {e}")
        return None
