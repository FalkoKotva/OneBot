"""Help cog for discord members who need help."""

import logging

import discord
from discord import app_commands
from discord import Interaction as Inter

from utils import normalized_name
from ui import EmbedPageManager, HelpChannelsEmbed
from . import BaseCog


log = logging.getLogger(__name__)


class HelpCog(BaseCog):
    """Help cog for discord members who need help."""

    # def __init__(self, bot):
    #     super().__init__(bot)

    group = app_commands.Group(
        name='help',
        description='help commands...'
    )

    @group.command(name='channels')
    async def channels(self, inter:Inter):
        """Get a list of all channels and their topics"""

        # Log the interaction including who used it
        name = normalized_name(inter.user, with_id=False)
        log.debug('%s requested help channels', name)

        sorted_channels: list[list[discord.TextChannel]] = []
        chars = 0  # The length of characters in the current page

        for channel in inter.guild.text_channels:

            log.debug('Checking channel: %s', channel.name)

            # Add the character counts to determine if the page is full
            chars += len(channel.name)
            if channel.topic:
                chars += len(channel.topic)

            # If this page is full or there or no pages,
            # create a new one
            if chars > 900 or not sorted_channels:
                sorted_channels.append([])
                chars = 0

            # Add the channel to the last page
            sorted_channels[-1].append(channel)

        # Create an embed for each page
        all_embeds = (
            HelpChannelsEmbed(channels) for channels in sorted_channels
        )

        # Create an object to manage the pages
        multi_embed = EmbedPageManager()
        multi_embed.add_embeds(*all_embeds)

        # Send the pages to the member
        await multi_embed.send(inter)


async def setup(bot):
    """Setup function"""

    cog = HelpCog(bot)
    await bot.add_cog(cog)
