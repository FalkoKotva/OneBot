"""Entry point for the bot. Run this file to get things started."""

import json
import logging
import discord
import asyncio

from bot import Bot
from logs import setup_logs
from constants import BAD_TOKEN, NO_TOKEN, NO_CONFIG


log = logging.getLogger('main')

async def main():

    # Get the bot config
    try:
        with open('./data/test.config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
    except FileNotFoundError:
        print(NO_CONFIG)
        return

    # Setup logging before anything else
    log_level = config['log_level']
    log_filepath = setup_logs(log_level=log_level)

    # Get the secret token
    try:
        with open('TOKEN', 'r', encoding='utf-8') as f:
            token = f.read()
    except FileNotFoundError:
        log.critical(NO_TOKEN)
        return

    # Initialize the bot
    async with Bot(config, log_filepath) as bot:

        # Load the bot's cogs
        await bot.load_cogs()

        # Startup the bot
        try:
            await bot.start(token, reconnect=True)
        except discord.LoginFailure:
            log.critical(BAD_TOKEN)

if __name__ == '__main__':
    asyncio.run(main())