# CarSaleWall

**CarSaleWall** is a Telegram channel automation that fetches the latest car listings from [Yad2](https://www.yad2.co.il/) and posts new car ads directly to a Telegram channel every 10 minutes. By integrating with GitHub Actions, the project ensures that your Telegram audience always stays up-to-date with the newest car offers—fully automated and hassle-free.

## Key Features

- **Regular Updates:** Fetches and posts new listings every 10 minutes.
- **Seamless Integration:** Uses GitHub Actions to schedule the scraping job—no separate servers required.
- **Rich Car Listing Data:** Displays the car’s make, model, year, mileage, price, contact details, and a direct link to the listing.
- **Automatic Telegram Posting:** Publishes the latest car ads to your Telegram channel, including the featured image, if available.

## Project Structure

The project is composed of two main directories:


1.**`src`**  
   Contains the core Python source code for scraping and posting.  
   - **scrapper.py**:  
     The main script that:
     - Retrieves updated car listings from Yad2.
     - Formats each listing.
     - Posts the listings (including images) to the specified Telegram channel.
   
   - **constants.py**:  
     Houses constant variables and keys used within the scraper for data extraction and formatting.

2.**`.github/workflows`**  
   Contains GitHub Actions configuration files that schedule and run the scraping job.  
   - **scrapper.yml**: Defines a workflow that:
     - Triggers every 10 minutes.
     - Installs dependencies.
     - Runs the `scrapper.py` script to fetch and post new listings to Telegram.

## How It Works

1. **Data Retrieval:**  
   `scrapper.py` sends a request to Yad2’s feed API to get the latest car listings.

2. **Data Parsing & Formatting:**  
   The script extracts essential details like manufacturer, model, year, mileage, price, and seller contact info. It then formats these details into a Telegram-friendly message with emojis for quick readability.

3. **Telegram Posting:**  
   Using the Telethon library, the script posts each new car advertisement to the Telegram channel `CarSaleWall`.

4. **Automation via GitHub Actions:**  
   The `scrapper.yml` workflow runs every 10 minutes. It:
   - Checks out the repository.
   - Sets up a Python environment.
   - Installs dependencies from `requirements.txt`.
   - Runs `scrapper.py` with the environment variables (`API_ID`, `API_HASH`, `BOT_TOKEN`, `POST_URL`) provided through GitHub Secrets.

## Requirements

- **Python 3.12+** (configurable in the GitHub workflow)
- **Dependencies:** Listed in `requirements.txt` (for example, `telethon`, `requests`, etc.)

## Environment Variables

In order to run `scrapper.py` successfully, you need to provide several environment variables through GitHub Secrets:

- `API_ID`: Your Telegram app’s API ID.
- `API_HASH`: Your Telegram app’s API Hash.
- `BOT_TOKEN`: The Telegram bot token provided by BotFather.
- `POST_URL`: The base URL to generate the final link for each car listing. Often this would be a URL pointing to the Yad2 listing details.

**Note:**  
These secrets are stored securely in your repository’s **Settings > Secrets and variables > Actions** section. The GitHub Actions workflow references them as `${{ secrets.API_ID }}`, `${{ secrets.API_HASH }}`, `${{ secrets.BOT_TOKEN }}`, and `${{ secrets.POST_URL }}`.

## Setup & Deployment

1. **Fork or Clone the Repository:**
   ```bash
   git clone https://github.com/hayuntal/CarSaleWall.git
   cd CarSaleWall
   ```

2. **Configure GitHub Secrets:**
   - Go to the repository’s **Settings > Secrets and variables > Actions**.
   - Add `API_ID`, `API_HASH`, `BOT_TOKEN`, `POST_URL` as repository secrets.

3. **Adjust the Schedule (Optional):**
   The workflow runs every 10 minutes by default. If you want to change this interval:
   - Open `.github/workflows/scrapper.yml`
   - Modify the `cron` schedule to your desired frequency.

4. **Trigger the Workflow:**
   By default, the workflow runs on schedule. You can also trigger it manually from the GitHub Actions tab.

## Contributing

Contributions are welcome! If you have ideas for new features, performance improvements, or bug fixes, feel free to open an issue or submit a pull request.

---

*Have additional questions or need clarifications? Feel free to ask!*