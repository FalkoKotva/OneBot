import pytest
import discord.ext.test as dpytest

import sys
# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.append('../src')

from bot import Bot

@pytest.fixture
def bot(event_loop):
    
    with Bot() as bot: # However you create your bot, make sure to use loop=event_loop
        
        dpytest.configure(bot)
        print("Hello")
        return bot


@pytest.mark.asyncio
async def test_ping(bot):
    await dpytest.message("!ping")
    assert dpytest.verify().message().contains().content("Ping:")


@pytest.mark.asyncio
async def test_foo(bot):
    await dpytest.message("!hello")
    assert dpytest.verify().message().content("Hello World!")