import pytest
import discord.ext.test as dpytest

import asyncio
from bot import Bot 

with open('C:\\Users\\ksang\\OneDrive\\Desktop\\ESS\\issue\\OneBot\\src\\TOKEN', 'r', encoding='utf-8') as file:
    token = file.read()

@pytest.fixture
def bot(event_loop):
    
    with Bot() as bot:
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