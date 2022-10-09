"""Entry point for the bot. Run this file to get things started."""

import json
import logging
import discord
import asyncio

from logs import setup_logs
from bot import Bot


log = logging.getLogger('main')

async def main():

    # Get the bot config
    try:
        with open('./data/test.config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
    except FileNotFoundError:
        print('CRITICAL ERROR: config file is missing! Shutting down...')
        return

    # Setup logging before anything else
    log_level = config['log_level']
    log_filepath = setup_logs(log_level=log_level)

    # Get the secret token
    try:
        with open('TOKEN', 'r', encoding='utf-8') as f:
            token = f.read()
    except FileNotFoundError:
        log.critical(
            'TOKEN file not found in project root! Shutting down...'
        )
        return

    # Initialize the bot
    async with Bot(config, log_filepath) as bot:

        # Load the bot's cogs
        await bot.load_cogs()

        # Startup the bot
        try:
            await bot.start(token, reconnect=True)
        except discord.LoginFailure:
            log.critical(
                'You have passed an improper or invalid token! '
                'Shutting down...'
            )

if __name__ == '__main__':
    asyncio.run(main())