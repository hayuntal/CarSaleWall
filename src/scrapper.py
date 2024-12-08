import os
import requests
import asyncio
import logging
import json

from telethon import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest
from constants import *

# Configuration
API_ID = list(str(os.getenv('API_ID')))
API_HASH = list(str(os.getenv('API_HASH')))
BOT_TOKEN = os.getenv('BOT_TOKEN')
POST_URL = os.getenv('POST_URL')

BASE_SHARE_URL = 'https://gw.yad2.co.il/feed-search-legacy/vehicles/cars'
CHANNEL_LINK = 't.me/carsalewall'

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_FILE = os.path.join(SCRIPT_DIR, '..', 'data', 'posted_cars.json')

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def join_channel(channel_link):
    """Attempts to join a Telegram channel."""
    try:
        await client(JoinChannelRequest(channel_link))
        logging.info(f"Successfully joined channel {channel_link}")
    except Exception as e:
        logging.error(f"Failed to join channel {channel_link}: {e}")

def load_posted_cars():
    """Load the list of posted cars from a JSON file."""
    if os.path.exists(DATASET_FILE):
        with open(DATASET_FILE, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def save_posted_cars(posted_cars):
    """Save the updated list of posted cars to a JSON file."""
    with open(DATASET_FILE, 'w', encoding='utf-8') as f:
        json.dump(posted_cars, f, ensure_ascii=False, indent=4)


def get_posts():
    try:
        response = requests.get(BASE_SHARE_URL)
        posts = response.json()[DATA][FEED][FEED_ITEMS]

        new_posts = []
        for post in posts:
            if post[TYPE] == AD:
                kilometer = f'{post[ROW3][2][4:]} {KM}' if len(post[ROW3]) >= 3 else NO_WRITTERN
                image = post[IMAGES][IMAGE1][SOURCE] if IMAGES in post and IMAGE1 in post[IMAGES] and SOURCE in \
                                                           post[IMAGES][IMAGE1] else None
                city = post[CITY] if CITY in post else NO_WRITTERN
                params = {
                    'Id': post[AD_NUMBER], 'Company': post[MANUFACTURER], 'Model': post[MODEL], 'Year': post[YEAR],
                    'Kilometers': kilometer, 'Price': post[PRICE], 'Yad': post[HAND],
                    'Contact Name': post[CONTACT], 'City': city, 'Image': image,
                    'Link': f"{POST_URL}/{post[ID]}"
                }
                new_posts.append(params)

        logging.info(f"Retrieved {len(new_posts)} new posts.")
        return new_posts
    except Exception as e:
        logging.error(f"Error retrieving posts: {e}")
        return []

def convert_format_to_telegram(post):
    """Change the format of each post, for Telegram post"""
    return (
        f"🚗 חברה: {post['Company']}\n"
        f"🚙 דגם: {post['Model']} ({post['Year']})\n"
        f"📏 קילומטראז': {post['Kilometers']}\n"
        f"🖐️ יד: {post['Yad']}\n"
        f"💰 מחיר: {post['Price']}\n\n"
        f"📞 איש קשר: {post['Contact Name']}\n"
        f"📍 איזור: {post['City']}\n"
        f"{post['Link']}"
    )

async def post_message(message, image_path):
    try:
        if image_path is not None:
            await client.send_file(CHANNEL_LINK, image_path, caption=message)
        else:
            await client.send_message(CHANNEL_LINK, message)
        logging.info("Message posted successfully")
    except Exception as e:
        logging.error(f"Failed to post message: {e}")

async def main():
    try:
        await client.start(bot_token=BOT_TOKEN)

        posted_cars = load_posted_cars()
        posted_links = {car['Link'] for car in posted_cars}

        posts = get_posts()
        new_posts = [p for p in posts if p['Link'] not in posted_links]

        if new_posts:
            for post in new_posts:
                format_message = convert_format_to_telegram(post)
                await post_message(format_message, post['Image'])

                # Add the newly posted car details to the dataset
                posted_cars.append(post)
                posted_links.add(post['Link'])

            # Save the updated posted cars list
            save_posted_cars(posted_cars)
            logging.info(f"All {len(new_posts)} new posts have been successfully sent and recorded.")
        else:
            logging.info("No new posts to send.")
    except asyncio.CancelledError:
        logging.error("The operation was cancelled.")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
    finally:
        await client.disconnect()
        logging.info("Client disconnected.")

if __name__ == "__main__":
    client = TelegramClient('bot_session', ''.join(API_ID), ''.join(API_HASH))
    asyncio.run(main())