import os
import logging
from typing import List, Dict, Any, Optional
import psycopg2
import pandas as pd
from ultralytics import YOLO
from .config import DBConfig, PathConfig, YOLO_MODEL_PATH
from .utils import setup_logging, get_db_connection

# Initialize Config
db_config = DBConfig()
path_config = PathConfig()

# Set up logging
setup_logging('yolo_detection.log')

def create_detection_table(conn: psycopg2.extensions.connection) -> None:
    """Creates the table for storing YOLO detections."""
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS raw.yolo_detections (
                    id SERIAL PRIMARY KEY,
                    message_id INTEGER,
                    channel_name TEXT,
                    image_path TEXT,
                    detected_objects TEXT, 
                    primary_class TEXT,
                    confidence_score FLOAT,
                    image_category TEXT, 
                    detection_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()
            logging.info("Table raw.yolo_detections created/verified.")
    except Exception as e:
        logging.error(f"Error creating table: {e}")
        conn.rollback()

def categorize_image(detections: List[Dict[str, Any]]) -> str:
    """
    Categorizes image based on detected objects.
    - Promotional: Person + (Bottle or Cup or Bowl or Box (if mapped))
    - Product Display: Bottle, Cup, Bowl, etc. NO Person
    - Lifestyle: Person, NO Product
    - Other: No significant objects or other objects
    """
    classes = [d['class'] for d in detections]
    
    has_person = 'person' in classes
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

def run_detection(conn: psycopg2.extensions.connection) -> None:
    """Runs YOLO detection on all images in the raw images directory."""
    model = YOLO(YOLO_MODEL_PATH)
    base_dir = path_config.IMAGE_DIR
    
    if not os.path.exists(base_dir):
        logging.error(f"Images directory not found at {base_dir}")
        return

    channels = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
    
    processed_count = 0
    all_detections: List[Dict[str, Any]] = []
    
    for channel in channels:
        channel_path = os.path.join(base_dir, channel)
        images = [f for f in os.listdir(channel_path) if f.endswith(('.jpg', '.jpeg', '.png'))]
        
        for img_file in images:
            img_path = os.path.join(channel_path, img_file)
            message_id_str = img_file.split('.')[0]
            try:
                message_id = int(message_id_str)
            except ValueError:
                logging.warning(f"Skipping image with invalid message ID name: {img_file}")
                continue
            
            try:
                # Run inference
                results = model(img_path)
                
                detections: List[Dict[str, Any]] = []
                for r in results:
                    for box in r.boxes:
                        cls_id = int(box.cls[0])
                        cls_name = model.names[cls_id]
                        conf = float(box.conf[0])
                        detections.append({'class': cls_name, 'conf': conf})
                
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
                
                with conn.cursor() as cur:
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
                
                all_detections.append({
                    'message_id': message_id,
                    'channel_name': channel,
                    'detected_class': primary_class,
                    'confidence_score': max_conf,
                    'image_category': category
                })
                
            except Exception as e:
                logging.error(f"Failed to process {img_path}: {e}")
                conn.rollback()

    # Save to CSV
    if all_detections:
        df = pd.DataFrame(all_detections)
        os.makedirs(path_config.PROCESSED_DATA, exist_ok=True)
        csv_path = os.path.join(path_config.PROCESSED_DATA, 'yolo_detections.csv')
        df.to_csv(csv_path, index=False)
        logging.info(f"Saved detection results to {csv_path}")
                
    logging.info(f"YOLO detection completed. Processed {processed_count} images.")
    print(f"Processed {processed_count} images.")

if __name__ == "__main__":
    connection = get_db_connection(db_config)
    if connection:
        create_detection_table(connection)
        run_detection(connection)
        connection.close()
