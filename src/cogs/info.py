"""Cog for info commands."""

import logging
import platform
import discord
from discord import app_commands, Interaction as Inter

from cog import Cog


log = logging.getLogger(__name__)


class InfoCog(Cog, name='Info'):
    """Cog for info commands."""

    def __init__(self, bot):
        super().__init__(bot=bot)
        self.get_app_commands()[0].guilds = (bot.main_guild.id,)

    @app_commands.command(name='info')
    async def get_all_info(self, inter:Inter):
        """Get all info on the bot."""

        py_ver = platform.python_version()
        system = platform.system()
        uptime = str(self.bot.uptime)

        embed = discord.Embed(
            title='Info',
            description='```'
            f'Python Ver: {py_ver}\n'
            f'System: {system}\n'
            f'Uptime: {uptime}\n'
            '```',
            colour=discord.Colour.blurple()
        )
        await inter.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(InfoCog(bot=bot))
