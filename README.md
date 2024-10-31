# Telegram Bot for monitoring the schedule

## Description
This project is a Telegram bot that monitors schedule changes in a specific Telegram channel and forwards the corresponding messages and photos to a group with participants. The bot responds to user commands in private messages and notifies about the status of its work.

## Functionality
- Forwards images with the schedule from the channel to the group.
- Notifies participants about changes made via hashtags: `#replacement`, `#replacements`, `#schedule`.
- Reacts to text messages with a group number (for example, "516").
- Responses to requests about the bot's status, regardless of the case of writing ("Are you working?") (in Russian).

## Installation
1. Clone the repository:
git clone https://github.com/Your_nickname/Your_repository.git
Go to the project directory:
cd Your_repository

Install the required libraries:
pip install -r requirements.txt

Usage
Run the bot using the command:
python bot.py
Type the /start command to activate the bot.
Use the /stop command to stop it.
Contribution
If you want to contribute to the project, please fork the repository and submit a pull request with your changes.

License
There is no license.