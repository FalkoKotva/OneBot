import pytest
import discord.ext.test as dpytest

import sys
# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, 'OneBot\\src')
import bot as b

token = "MTAzOTQ1MzYxODk1NDMxNzgzNA.GDtMgo.pct3HlmH9a42rLQJKOBUOYdikK4uqT-MmDQEBQ"

@pytest.fixture
def bot(event_loop):
    
    with b.Bot() as bot:
        bot.load_extensions()
        bot.start(token, reconnect=True) # However you create your bot, make sure to use loop=event_loop
        dpytest.configure(bot)
        return bot


@pytest.mark.asyncio
async def test_ping(bot):
    await dpytest.message("!ping")
    assert dpytest.verify().message().contains().content("Ping:")


@pytest.mark.asyncio
async def test_foo(bot):
    await dpytest.message("!hello")
    assert dpytest.verify().message().content("Hello World!")