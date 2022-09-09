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


async def main():
    """
    Main function.
    """

    # Create the bot
    bot = commands.Bot(
        command_prefix='!', intents=discord.Intents().all()
    )
    bot.remove_command('help')  # we wont be needing this
    
    # Load the cogs
    for filename in os.listdir('./src/cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')

    @bot.event
    async def on_ready():
        """
        Automatically called when the bot is ready.
        Prints a ready message to the console.
        """
        output = f'Logged in as {bot.user} (ID: {bot.user.id})'
        print(output)

    # Startup the bot using the hidden token
    with open('TOKEN', 'r', encoding='utf-8') as f:
        token = f.read()

    await bot.start(token=token)


if __name__ == '__main__':
    asyncio.run(main())