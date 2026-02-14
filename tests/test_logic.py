import pytest
import os
from src.yolo_detect import categorize_image
from src.config import DBConfig, PathConfig

def test_categorize_image_promotional():
    detections = [{'class': 'person', 'conf': 0.9}, {'class': 'bottle', 'conf': 0.8}]
    assert categorize_image(detections) == 'Promotional'

def test_categorize_image_product():
    detections = [{'class': 'bottle', 'conf': 0.8}, {'class': 'cup', 'conf': 0.7}]
    assert categorize_image(detections) == 'Product Display'

def test_categorize_image_lifestyle():
    detections = [{'class': 'person', 'conf': 0.9}]
    assert categorize_image(detections) == 'Lifestyle'

def test_categorize_image_other():
    detections = [{'class': 'car', 'conf': 0.5}]
    assert categorize_image(detections) == 'Other'

def test_config_defaults():
    config = DBConfig()
    # Check if a default exists (this helps verify env loading or fallback)
    assert config.port in ['5433', os.getenv('DB_PORT')]
    
def test_path_config():
    paths = PathConfig()
    assert paths.RAW_DATA == 'data/raw'
    assert 'images' in paths.IMAGE_DIR

