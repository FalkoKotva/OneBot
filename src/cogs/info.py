"""Cog for info commands."""

import time
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

        dpy_ver = discord.__version__
        py_ver = platform.python_version()
        uptime = str(self.bot.uptime)
        start_time = str(self.bot.start_time)

        embed = discord.Embed(
            title='Server Details',
            description='```'
            f'Python Ver: {py_ver}\n'
            f'Discord.py Ver: {dpy_ver}\n'
            '---\n'
            f'OS: {platform.system()}\n'
            f'OS Ver: {platform.version()}\n'
            '---\n'
            f'Uptime: {uptime}\n'
            f'Started: {start_time}\n'
            f'Timezone: {time.tzname[1]}\n'
            '```',
            colour=discord.Colour.blurple()
        )
        await inter.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(InfoCog(bot=bot))
