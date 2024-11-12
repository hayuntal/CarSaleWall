import os
import requests
import pandas as pd

from telethon import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest

# Configuration
DATA_PATH = os.getenv('DATA_PATH')
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
PHONE_NUMBER = os.getenv('PHONE_NUMBER')
CHANNEL_LINK = 't.me/carscoutbott'

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
    url = 'https://gw.yad2.co.il/feed-search-legacy/vehicles/cars'
    response = requests.get(url)
    posts = response.json()['data']['feed']['feed_items']

    data = load_data()
    new_posts = []

    for post in posts:

        if (post['type'] == 'ad') and (post['id'] not in data['Id'].values):
            kilometer = (post['row_3'][2][4:] + ' ק"מ ') if len(post['row_3']) >= 3 else "לא צוין"

            image = post['images']['Image1']['src'] if 'images' in post and 'Image1' in post['images'] and 'src' in \
                                                       post['images']['Image1'] else None

            city = post['city'] if 'city' in post else 'לא צוין'
            params = {
                'Id': post['id'], 'Company': post['manufacturer'], 'Model': post['model'], 'Year': post['year'],
                'Kilometers': kilometer, 'Price': post['price'], 'Yad': post['Hand_text'],
                'Contact Name': post['contact_name'], 'City': city, 'Image': image
            }
            new_posts.append(params)

    return new_posts


def load_data():
    """Loads existing data from a CSV file."""
    df = pd.read_csv(DATA_PATH)
    return df

def update_data(posts):
    """
    Updates the current dataframes, with the new posts
    """
    new_posts_df = pd.DataFrame(posts)[['Id', 'Company', 'Model', 'Kilometers', 'Price', 'Yad', 'Contact Name']] # New posts into dataframe
    prev_posts_df = load_data() # Load the exists dataframe

    updated_df = pd.concat([prev_posts_df, new_posts_df], ignore_index=False) # Merge the previous and current posts
    updated_df.to_csv(DATA_PATH, index=False) # Save the updated dataframe into the csv file

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
        f"📍 איזור: {post['City']}"
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
    await client.start()
    await join_channel(CHANNEL_LINK) # Join to 'CarScoutBot channel'

    posts = get_posts()  # Get the new posts via Yad2

    if len(posts) != 0:
        for post in posts:
            format_message = convert_format_to_telegram(post)
            await post_message(format_message, post['Image']) # Post to Telegram channel
        print(f"All {len(posts)} posts have been successfully sent and data updated.")
        update_data(posts)
    else:
        print("No posts to send.")


if __name__ == "__main__":
    with client:
        client.loop.run_until_complete(main())