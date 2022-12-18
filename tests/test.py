import discord
import discord.ext.commands as commands

import pytest
import pytest_asyncio
import discord.ext.test as dpytest

""" sys.path.append("..scr/")
from bot import Bot """

from conftest import bot as bb

@pytest.mark.asyncio
async def test_ping(bb):
    await dpytest.message("!ping")
    assert dpytest.verify().message().content("Pong !")


@pytest.mark.asyncio
async def test_echo(bb):
    await dpytest.message("!echo Hello world")
    assert dpytest.verify().message().contains().content("Hello")