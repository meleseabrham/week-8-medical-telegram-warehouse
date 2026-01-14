import os
import json
import logging
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5433')
DB_NAME = os.getenv('DB_NAME', 'medical_db')
DB_USER = os.getenv('DB_USER', 'user')
DB_PASS = os.getenv('DB_PASS', 'password')

# Set up logging
logging.basicConfig(
    filename='logs/loading.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def connect_db():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        return conn
    except Exception as e:
        logging.error(f"Error connecting to database: {e}")
        return None

def create_raw_schema(conn):
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

def load_data(conn):
    base_dir = 'data/raw/telegram_messages'
    if not os.path.exists(base_dir):
        logging.warning("No telegram_messages directory found.")
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
    connection = connect_db()
    if connection:
        create_raw_schema(connection)
        load_data(connection)
        connection.close()
