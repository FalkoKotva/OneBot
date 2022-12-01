import pytest
import discord.ext.test as dpytest


@pytest.fixture
def bot(event_loop):
    bot = ... # However you create your bot, make sure to use loop=event_loop
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