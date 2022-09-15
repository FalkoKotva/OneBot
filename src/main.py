"""
Entry point for the bot. Run this file to get things started.

I am unable to use logging with this bot because the code runs asynchronously
which is not supported by the built-in logging library. As a substititue until
I find a better solution, I will be using print functions.
"""


import os
import asyncio
import discord
from discord.ext import commands

from constants import GUILD_ID


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

        print(f'Logged in as {self.user} (ID: {self.user.id})')
    
    async def load_cogs(self):
        """
        Attempts to load all .py files in the cogs directory as cogs.
        """

        for filename in os.listdir('./src/cogs'):
            if filename.endswith('.py'):
                await self.load_extension(f'cogs.{filename[:-3]}')


async def main():

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