import os
import requests
import pandas as pd

from telethon import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest
from constants import *

# Configuration
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
PHONE_NUMBER = os.getenv('PHONE_NUMBER')
CHANNEL_LINK = 't.me/carscoutbott'
BASE_SHARE_URL = 'https://www.yad2.co.il/vehicles/item'

# Initialize the Telegram client
client = TelegramClient('session_name', API_ID, API_HASH)


async def join_channel(channel_link):
    """Attempts to join a Telegram channel."""
    try:
        await client(JoinChannelRequest(channel_link))
        print(f'Successfully Joined Channel {channel_link}')
    except:
        print(f'Failed to Join Channel {channel_link}')


def get_posts():
    # TODO READ USER INPUT
    # FILTERS = EXTRACT FILTERS FROM USER INPUT

    url = 'https://gw.yad2.co.il/feed-search-legacy/vehicles/cars'
    # url = 'https://gw.yad2.co.il/feed-search-legacy/vehicles/cars?manufacturer=5%2C54%2C12&price=-1-160000'

    response = requests.get(url)
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
                'Link': f"{BASE_SHARE_URL}/{post[ID]}"
            }
            new_posts.append(params)

    return new_posts

def convert_format_to_telegram(post):
    """
    Change the format of each post, for telegram post
    """
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
            await client.send_file(CHANNEL_LINK, image_path, caption=message) # Post with a car image
        else:
            await client.send_message(CHANNEL_LINK, message) # Post without a car image
            print(f"Message posted successfully in {CHANNEL_LINK}")
    except Exception as e:
        print(f"Failed to post message in {CHANNEL_LINK}: {e}")


async def main():
    await client.start(phone=lambda: PHONE_NUMBER)
    await join_channel(CHANNEL_LINK) # Join to 'CarScoutBot channel'

    posts = get_posts()  # Get the new posts via Yad2

    if len(posts) != 0:
        for post in posts:
            format_message = convert_format_to_telegram(post)
            await post_message(format_message, post['Image']) # Post to Telegram channel
        print(f"All {len(posts)} posts have been successfully sent and data updated.")
    else:
        print("No posts to send.")


if __name__ == "__main__":
    with client:
        client.loop.run_until_complete(main())
