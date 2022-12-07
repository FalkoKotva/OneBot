"""Entry point for the bot, run this file to get things started."""

import asyncio

from bot import Bot

async def main():
    """Main function for starting the application"""

    # You will need to create this file if it doesn't exist
    # and paste your bot token in it.
    with open('OneBot/src/TOKEN', 'r', encoding='utf-8') as file:
        token = file.read()

    # Construct the bot, load the extensions and start er up.
    async with Bot() as bot:
        await bot.load_extensions()
        await bot.start(token, reconnect=True)


if __name__ == '__main__':
    asyncio.run(main())
