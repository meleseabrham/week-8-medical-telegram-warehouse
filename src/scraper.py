import os
import json
import logging
import asyncio
from datetime import datetime
from telethon import TelegramClient, events
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_ID = os.getenv('TG_API_ID')
API_HASH = os.getenv('TG_API_HASH')

# List of channels to scrape
CHANNELS = [
    'CheMed123',
    'lobelia4cosmetics',
    'tikvahpharma',
    'yenehealth',
    'LiyuPharma'
]

STATE_FILE = 'data/scraping_state.json'

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=4)

# Set up logging
logging.basicConfig(
    filename='logs/scraping.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

async def scrape_channel(client, channel_username, last_id=0):
    """Scrapes messages and images from a given Telegram channel."""
    logging.info(f"Starting scraping for channel: {channel_username} (last_id: {last_id})")
    
    try:
        entity = await client.get_entity(channel_username)
        channel_name = entity.username or entity.title
        
        # Create folder for images
        image_dir = f'data/raw/images/{channel_name}'
        os.makedirs(image_dir, exist_ok=True)
        
        messages = []
        new_last_id = last_id
        
        # iter_messages with min_id to only get newer messages
        async for message in client.iter_messages(entity, min_id=last_id, limit=200):
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
        json_dir = f'data/raw/telegram_messages/{today}'
        os.makedirs(json_dir, exist_ok=True)
        
        json_path = os.path.join(json_dir, f"{channel_name}.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(messages, f, indent=4, ensure_ascii=False)
            
        logging.info(f"Successfully scraped {len(messages)} messages from {channel_name}")
        return channel_username, new_last_id
        
    except Exception as e:
        logging.error(f"Error scraping {channel_username}: {str(e)}")
        return channel_username, last_id

async def main():
    # Attempting another set of parameters to bypass RPC Error 406
    async with TelegramClient(
        'scraping_session', 
        API_ID, 
        API_HASH,
        device_model='iPhone 13 Pro',
        system_version='15.0',
        app_version='8.2.1',
        lang_code='en',
        system_lang_code='en-US'
    ) as client:
        state = load_state()
        tasks = []
        for channel in CHANNELS:
            last_id = state.get(channel, 0)
            tasks.append(scrape_channel(client, channel, last_id))
            
        results = await asyncio.gather(*tasks)
        
        # Update and save state
        for channel, nid in results:
            state[channel] = nid
        save_state(state)

if __name__ == '__main__':
    if not API_ID or not API_HASH:
        print("API_ID and API_HASH must be set in .env file")
        logging.error("API_ID or API_HASH missing in .env")
    else:
        asyncio.run(main())
