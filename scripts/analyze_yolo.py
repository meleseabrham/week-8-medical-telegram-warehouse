import os
import psycopg2
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5433')
DB_NAME = os.getenv('DB_NAME', 'medical_db')
DB_USER = os.getenv('DB_USER', 'sa')
DB_PASS = os.getenv('DB_PASS', '123')

def analyze():
    try:
        conn = psycopg2.connect(
            host=DB_HOST, port=DB_PORT, database=DB_NAME, user=DB_USER, password=DB_PASS
        )
        
        # Query: Average views per image category
        query = """
        SELECT 
            image_category,
            COUNT(*) as post_count,
            ROUND(AVG(m.views)) as avg_views
        FROM raw.yolo_detections d
        JOIN raw.telegram_messages m ON d.message_id::TEXT = m.id::TEXT AND d.channel_name = m.channel_name
        GROUP BY image_category
        ORDER BY avg_views DESC;
        """
        
        df = pd.read_sql(query, conn)
        print("\n--- Insight: Average Views by Image Category ---")
        print(df)
        
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    analyze()
