"""
Entry point for the bot. Run this file to get things started.
"""


import os
import asyncio
import logging
import discord
from discord.ext import commands

from constants import GUILD_ID
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
        
        # The main guild is the DCG server which this bot is made for
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
            log.debug('Tree Commands Synced')

        log.info(f'Logged in as {self.user} (ID: {self.user.id})')
    
    async def load_cogs(self):
        """
        Attempts to load all .py files in the cogs directory as cogs.
        """

        for filename in os.listdir('./src/cogs'):
            if filename.endswith('.py'):
                await self.load_extension(f'cogs.{filename[:-3]}')
                log.debug(f'Loading Cog: {filename}')


async def main():
    
    # Setup logging before anything else
    setup_logs()
    
    # Get the root logger
    global log
    log = logging.getLogger('main')

    # Mute the loud discord.py logger
    discord_logger = logging.getLogger('discord')
    discord_logger.setLevel(logging.WARNING)

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