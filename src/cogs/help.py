"""Help cog for discord members who need help."""

import discord
from discord import app_commands
from discord import Interaction as Inter

from ui import HelpChannelsEmbed
from . import BaseCog


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

        embed = HelpChannelsEmbed(inter.guild.channels)
        await inter.response.send_message(embed=embed, ephemeral=True)




async def setup(bot):
    """Setup function"""

    cog = HelpCog(bot)
    await bot.add_cog(cog)
