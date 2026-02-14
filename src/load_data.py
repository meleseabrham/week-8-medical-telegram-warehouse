import os
import json
import logging
from typing import Optional
import psycopg2
from .config import DBConfig, PathConfig
from .utils import setup_logging, get_db_connection

# Initialize Config
db_config = DBConfig()
path_config = PathConfig()

# Set up logging
setup_logging('loading.log')

def create_raw_schema(conn: psycopg2.extensions.connection) -> None:
    """Creates the raw schema and necessary tables for storing scraped data."""
    try:
        with conn.cursor() as cur:
            cur.execute("CREATE SCHEMA IF NOT EXISTS raw;")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS raw.telegram_messages (
                    id SERIAL PRIMARY KEY,
                    message_id INTEGER,
                    channel_name TEXT,
                    message_date TIMESTAMP,
                    message_text TEXT,
                    has_media BOOLEAN,
                    image_path TEXT,
                    views INTEGER,
                    forwards INTEGER
                );
            """)
            conn.commit()
            logging.info("Raw schema and table created successfully.")
    except Exception as e:
        logging.error(f"Error creating schema: {e}")
        conn.rollback()

def load_data(conn: psycopg2.extensions.connection) -> None:
    """Reads JSON files from the raw data directory and inserts them into the database."""
    base_dir = path_config.MESSAGES_DIR
    if not os.path.exists(base_dir):
        logging.warning(f"No messages directory found at {base_dir}")
        return

    try:
        with conn.cursor() as cur:
            for date_folder in os.listdir(base_dir):
                date_path = os.path.join(base_dir, date_folder)
                if os.path.isdir(date_path):
                    for json_file in os.listdir(date_path):
                        if json_file.endswith('.json'):
                            file_path = os.path.join(date_path, json_file)
                            with open(file_path, 'r', encoding='utf-8') as f:
                                messages = json.load(f)
                                for msg in messages:
                                    cur.execute("""
                                        INSERT INTO raw.telegram_messages (
                                            message_id, channel_name, message_date, 
                                            message_text, has_media, image_path, views, forwards
                                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                                    """, (
                                        msg.get('message_id'),
                                        msg.get('channel_name'),
                                        msg.get('message_date'),
                                        msg.get('message_text'),
                                        msg.get('has_media'),
                                        msg.get('image_path'),
                                        msg.get('views'),
                                        msg.get('forwards')
                                    ))
            conn.commit()
            logging.info("Data loaded successfully into raw.telegram_messages.")
    except Exception as e:
        logging.error(f"Error loading data: {e}")
        conn.rollback()

if __name__ == "__main__":
    connection = get_db_connection(db_config)
    if connection:
        create_raw_schema(connection)
        load_data(connection)
        connection.close()
