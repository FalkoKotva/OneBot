"""Module for retrieving objects using the cache or the discord API."""

import logging
import discord
from discord.ext.commands import Bot


log = logging.getLogger(__name__)


class Get:
    """Class for retrieving objects using the cache or the discord API."""

    def __init__(self, bot:Bot):
        self.bot = bot

    async def guild(self, _id:int, /) -> discord.Guild | None:
        """Get a discord guild object from an ID.

        Args:
            id (int): The ID of the guild.
        Returns:
            discord.Guild: The guild object.
            None: If the guild is not found.
        """

        log.debug('Getting guild object')
        guild_obj = self.bot.get_guild(_id)
        return guild_obj or await self.bot.fetch_guild(_id)


    async def channel(self, _id:int, /) -> discord.TextChannel | None:
        """Get a discord channel object from an ID.

        Args:
            id (int): The ID of the channel.
        Returns:
            discord.TextChannel: The channel object.
            None: If the channel is not found.
        """

        log.debug('Getting channel object')
        channel_obj = self.bot.get_channel(_id)
        return channel_obj or await self.bot.fetch_channel(_id)
