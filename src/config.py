import os
from dataclasses import dataclass, field
from typing import List
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class DBConfig:
    host: str = os.getenv('DB_HOST', 'localhost')
    port: str = os.getenv('DB_PORT', '5433')
    name: str = os.getenv('DB_NAME', 'medical_db')
    user: str = os.getenv('DB_USER', 'sa')
    password: str = os.getenv('DB_PASS', '123')

    @property
    def connection_string(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"

@dataclass(frozen=True)
class TelegramConfig:
    api_id: str = os.getenv('TG_API_ID')
    api_hash: str = os.getenv('TG_API_HASH')
    channels: List[str] = field(default_factory=lambda: [
        'CheMed123',
        'lobelia4cosmetics',
        'tikvahpharma',
        'yenehealth',
        'LiyuPharma'
    ])

@dataclass(frozen=True)
class PathConfig:
    RAW_DATA: str = 'data/raw'
    PROCESSED_DATA: str = 'data/processed'
    LOGS: str = 'logs'
    STATE_FILE: str = 'data/scraping_state.json'
    IMAGE_DIR: str = 'data/raw/images'
    MESSAGES_DIR: str = 'data/raw/telegram_messages'

# Constants
DEFAULT_LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
SCRAPING_LIMIT = 200
YOLO_MODEL_PATH = "yolov8n.pt"
