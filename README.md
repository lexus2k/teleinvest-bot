# teleinvest-bot

Telegram trade statistics reporting bot. The bot reports statistics once a day at specified time to
telegram channel. It can accept commands and answer to them.
Investment portfolio is taken from Google Sheets document.

## Usage

1. Create telegram bot as described in Telegram docs
2. Put the bot token to config.ini `telegram_bot_token` field
3. Create telegram channel as described in Telegram docs.
4. Add your newly created bot to the created telegram channel
5. Put telegram channel id to the config.ini `main_chat_id` field
6. Create new project in Google Cloud Platform console
7. Add yourself as the project owner
8. Enable Google Drive and Google Sheets API for the project
9. Add new OAuth client for the project and download client_secret.json to the bot folder
10. Create Google Sheets document, containing your Investment portfolio
11. Put Google Sheets document name to config.ini `sheets` field
12. Run the bot `python telegram_bot.py`
13. Follow the instructions in the python console

## Dependencies

* requests
* pygsheets
