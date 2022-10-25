"""Entry point for the bot. Run this file to get things started."""

import json
import logging
import asyncio
import discord

from bot import Bot
from logs import setup_logs
from constants import BAD_TOKEN, NO_TOKEN


log = logging.getLogger('main')

async def main():
    """Main function for starting the application"""

    # Setup logging before anything else
    log_filepath = setup_logs(log_level=logging.DEBUG)

    # Get the secret token
    try:
        with open('TOKEN', 'r', encoding='utf-8') as file:
            token = file.read()
    except FileNotFoundError:
        log.critical(NO_TOKEN)
        return

    # Initialize the bot
    async with Bot(log_filepath) as bot:

        # Load the bot's cogs
        await bot.load_cogs()

        # Startup the bot
        try:
            await bot.start(token, reconnect=True)
        except discord.LoginFailure:
            log.critical(BAD_TOKEN)

if __name__ == '__main__':
    asyncio.run(main())
