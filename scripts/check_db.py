import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5433')
DB_NAME = os.getenv('DB_NAME', 'medical_db')
DB_USER = os.getenv('DB_USER', 'sa')
DB_PASS = os.getenv('DB_PASS', '123')

def check_db():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        with conn.cursor() as cur:
            # Check Schemas
            cur.execute("SELECT schema_name FROM information_schema.schemata;")
            schemas = cur.fetchall()
            print(f"Schemas found: {[s[0] for s in schemas]}")
            
            # Check Tables in raw
            cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'raw';")
            raw_tables = cur.fetchall()
            print(f"Tables in 'raw' schema: {[t[0] for t in raw_tables]}")
            
            # Check Tables in public
            cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
            public_tables = cur.fetchall()
            print(f"Tables in 'public' schema: {[t[0] for t in public_tables]}")
            
            if raw_tables:
                cur.execute("SELECT count(*) FROM raw.telegram_messages;")
                count = cur.fetchone()[0]
                print(f"Rows in raw.telegram_messages: {count}")
                
                # Check YOLO Detections
                cur.execute("SELECT count(*) FROM raw.yolo_detections;")
                yolo_count = cur.fetchone()[0]
                print(f"Rows in raw.yolo_detections: {yolo_count}")

        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_db()
