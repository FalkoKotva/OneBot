
import pytest
import discord.ext.test as dpytest

from bot import Bot

with open('C:\\Users\\ksang\\Desktop\\ESS\\issue\\OneBot\\src\\TOKEN', 'r', encoding='utf-8') as file:
    token = file.read()

@pytest.fixture
def bot(event_loop):
    bot = Bot()
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