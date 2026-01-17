import os
import cv2
import logging
import psycopg2
import pandas as pd
from ultralytics import YOLO
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5433')
DB_NAME = os.getenv('DB_NAME', 'medical_db')
DB_USER = os.getenv('DB_USER', 'sa')
DB_PASS = os.getenv('DB_PASS', '123')

# Set up logging
logging.basicConfig(
    filename='logs/yolo_detection.log',
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

def create_detection_table(conn):
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS raw.yolo_detections (
                    id SERIAL PRIMARY KEY,
                    message_id INTEGER,
                    channel_name TEXT,
                    image_path TEXT,
                    detected_objects TEXT, -- Stores JSON string of detected objects like {'person': 0.9, 'bottle': 0.8}
                    primary_class TEXT,
                    confidence_score FLOAT,
                    image_category TEXT, -- 'Promotional', 'Product Display', 'Lifestyle', 'Other'
                    detection_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()
            logging.info("Table raw.yolo_detections created/verified.")
    except Exception as e:
        logging.error(f"Error creating table: {e}")
        conn.rollback()

def categorize_image(detections):
    """
    Categorizes image based on detected objects.
    - Promotional: Person + (Bottle or Cup or Bowl or Box (if mapped))
    - Product Display: Bottle, Cup, Bowl, etc. NO Person
    - Lifestyle: Person, NO Product
    - Other: No significant objects or other objects
    """
    classes = [d['class'] for d in detections]
    
    has_person = 'person' in classes
    # Common objects that might represent medical products in general YOLO context
    product_classes = ['bottle', 'cup', 'bowl', 'wine glass', 'vase', 'suitcase', 'handbag', 'backpack'] 
    
    has_product = any(cls in product_classes for cls in classes)
    
    if has_person and has_product:
        return 'Promotional'
    elif has_product and not has_person:
        return 'Product Display'
    elif has_person and not has_product:
        return 'Lifestyle'
    else:
        return 'Other'

def run_detection(conn):
    model = YOLO("yolov8n.pt")  # Load pre-trained model
    base_dir = 'data/raw/images'
    
    if not os.path.exists(base_dir):
        logging.error("Images directory not found.")
        return

    channels = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
    
    processed_count = 0
    
    for channel in channels:
        channel_path = os.path.join(base_dir, channel)
        images = [f for f in os.listdir(channel_path) if f.endswith(('.jpg', '.jpeg', '.png'))]
        
        for img_file in images:
            img_path = os.path.join(channel_path, img_file)
            message_id = img_file.split('.')[0]
            
            try:
                # Run inference
                results = model(img_path)
                
                detections = []
                for r in results:
                    for box in r.boxes:
                        cls_id = int(box.cls[0])
                        cls_name = model.names[cls_id]
                        conf = float(box.conf[0])
                        detections.append({'class': cls_name, 'conf': conf})
                
                # Determine primary detection (highest confidence)
                if detections:
                    best_detection = max(detections, key=lambda x: x['conf'])
                    primary_class = best_detection['class']
                    max_conf = best_detection['conf']
                    detected_str = str([d['class'] for d in detections])
                else:
                    primary_class = 'None'
                    max_conf = 0.0
                    detected_str = '[]'
                
                category = categorize_image(detections)
                
                # Save to DB
                with conn.cursor() as cur:
                    # Check if already exists to avoid duplicates (optional, strictly raw usually just inserts)
                    # For exercise, let's insert or ignore/update ideally, but simplistic insert here
                    # We will delete existing for this message_id/channel to allow re-runs
                    cur.execute("DELETE FROM raw.yolo_detections WHERE message_id = %s AND channel_name = %s", (message_id, channel))
                    
                    cur.execute("""
                        INSERT INTO raw.yolo_detections (
                            message_id, channel_name, image_path, detected_objects, 
                            primary_class, confidence_score, image_category
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (
                        message_id, channel, img_path, detected_str, 
                        primary_class, max_conf, category
                    ))
                conn.commit()
                processed_count += 1
                
            except Exception as e:
                logging.error(f"Failed to process {img_path}: {e}")
                conn.rollback()
                
    logging.info(f"YOLO detection completed. Processed {processed_count} images.")
    print(f"Processed {processed_count} images.")

if __name__ == "__main__":
    connection = connect_db()
    if connection:
        create_detection_table(connection)
        run_detection(connection)
        connection.close()
