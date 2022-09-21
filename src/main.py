"""
Entry point for the bot. Run this file to get things started.
"""


import os
import asyncio
import logging
import discord
from discord.ext import commands

from database import setup as db_setup
from constants import DATABASE, GUILD_ID
from logs import setup_logs


class Bot(commands.Bot):
    """
    This class is the root of the bot, all cogs are loaded from here.
    """

    # Discordpy doesnt automatically sync commands so we need a check
    commands_synced = False
    
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix='!', intents=intents)

        # Create the database file if it doesnt exist
        if not os.path.exists(DATABASE):
            db_setup()

        # Main discord server the bot is in
        self.main_guild = discord.Object(id=GUILD_ID)

    async def on_ready(self):
        """
        Called when the bot logs in.
        Syncs slash commands and prints a ready message.
        """

        # Sync slash commands
        await self.wait_until_ready()
        if not self.commands_synced:
            await self.tree.sync(guild=self.main_guild)
            self.commands_synced = True
            log.info('Tree Commands Synced')

        log.info(f'Logged in as {self.user} (ID: {self.user.id})')
    
    async def load_cogs(self):
        """
        Attempts to load all .py files in the cogs directory as cogs.
        """

        log.info('Loading cogs...')
        for filename in os.listdir('./src/cogs'):
            if filename.endswith('.py'):
                await self.load_extension(f'cogs.{filename[:-3]}')
                log.debug(f'Loading Cog: {filename}')
                continue
            
            log.warning(f'Found a non .py file in the cogs directory: {filename}, skipping...')


async def main():
    
    # Setup logging before anything else
    setup_logs()
    
    # Get the root logger
    global log
    log = logging.getLogger('main')

    # Get the secret token
    with open('TOKEN', 'r', encoding='utf-8') as f:
        token = f.read()

    bot = Bot()

    # Startup the bot    
    async with bot:
        bot.tree.copy_global_to(guild=bot.main_guild)
        await bot.load_cogs()
        await bot.start(token)

if __name__ == '__main__':
    asyncio.run(main())