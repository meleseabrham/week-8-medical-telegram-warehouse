import os
import json
import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional
from telethon import TelegramClient
from .config import TelegramConfig, PathConfig, SCRAPING_LIMIT
from .utils import setup_logging

# Initialize Config
tg_config = TelegramConfig()
path_config = PathConfig()

# Set up logging
setup_logging('scraping.log')

def load_state() -> Dict[str, int]:
    """Loads the last scraped message ID for each channel."""
    if os.path.exists(path_config.STATE_FILE):
        try:
            with open(path_config.STATE_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Error loading state file: {e}")
            return {}
    return {}

def save_state(state: Dict[str, int]) -> None:
    """Saves the last scraped message ID for each channel."""
    os.makedirs(os.path.dirname(path_config.STATE_FILE), exist_ok=True)
    with open(path_config.STATE_FILE, 'w') as f:
        json.dump(state, f, indent=4)

async def scrape_channel(client: TelegramClient, channel_username: str, last_id: int = 0) -> Tuple[str, int]:
    """Scrapes messages and images from a given Telegram channel."""
    logging.info(f"Starting scraping for channel: {channel_username} (last_id: {last_id})")
    
    try:
        entity = await client.get_entity(channel_username)
        channel_name = entity.username or entity.title
        
        # Create folder for images
        image_dir = os.path.join(path_config.IMAGE_DIR, channel_name)
        os.makedirs(image_dir, exist_ok=True)
        
        messages: List[Dict[str, Any]] = []
        new_last_id = last_id
        
        # iter_messages with min_id to only get newer messages
        async for message in client.iter_messages(entity, min_id=last_id, limit=SCRAPING_LIMIT):
            if message.id > new_last_id:
                new_last_id = message.id
                
            message_data = {
                'message_id': message.id,
                'channel_name': channel_name,
                'message_date': message.date.isoformat(), 
                'message_text': message.message or "",
                'has_media': message.media is not None,
                'views': message.views or 0,
                'forwards': message.forwards or 0,
            }
            
            # Download media if present
            if message.photo:
                image_path = os.path.join(image_dir, f"{message.id}.jpg")
                await client.download_media(message.photo, file=image_path)
                message_data['image_path'] = image_path
                logging.info(f"Downloaded image for message {message.id} in {channel_name}")
            
            messages.append(message_data)
        
        # Store metadata in partitioned JSON
        today = datetime.now().strftime('%Y-%m-%d')
        json_dir = os.path.join(path_config.MESSAGES_DIR, today)
        os.makedirs(json_dir, exist_ok=True)
        
        json_path = os.path.join(json_dir, f"{channel_name}.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(messages, f, indent=4, ensure_ascii=False)
            
        logging.info(f"Successfully scraped {len(messages)} messages from {channel_name}")
        return channel_username, new_last_id
        
    except Exception as e:
        logging.error(f"Error scraping {channel_username}: {str(e)}")
        return channel_username, last_id

async def run_scraper() -> None:
    """Main entry point for the scraping process."""
    if not tg_config.api_id or not tg_config.api_hash:
        logging.error("TG_API_ID or TG_API_HASH missing in .env")
        print("API_ID and API_HASH must be set in .env file")
        return

    async with TelegramClient(
        'scraping_session', 
        tg_config.api_id, 
        tg_config.api_hash,
        device_model='iPhone 13 Pro',
        system_version='15.0',
        app_version='8.2.1',
        lang_code='en',
        system_lang_code='en-US'
    ) as client:
        state = load_state()
        tasks = []
        for channel in tg_config.channels:
            last_id = state.get(channel, 0)
            tasks.append(scrape_channel(client, channel, last_id))
            
        results = await asyncio.gather(*tasks)
        
        # Update and save state
        for channel, nid in results:
            state[channel] = nid
        save_state(state)

if __name__ == '__main__':
    asyncio.run(run_scraper())

