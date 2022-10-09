"""Cog for info commands."""

import time
import logging
import platform
import discord
from discord import app_commands, Interaction as Inter

from . import BaseCog
from utils import check_is_owner


log = logging.getLogger(__name__)


class InfoCog(BaseCog, name='Server'):
    """Cog for info commands."""

    def __init__(self, bot):
        super().__init__(bot=bot)

    group = app_commands.Group(
        name='server',
        description='Server commands'
    )

    def _get_data(self) -> dict:
        return {
            'Bot': {
                'Name': self.bot.user.name,
                'Descriminator': f'#{self.bot.user.discriminator}',
                'ID': self.bot.user.id,
            },
            'Dependencies': {
                'Python': platform.python_version(),
                'Discord.py': discord.__version__,
            },
            'Server': {
                'OS': platform.system(),
                'OS Version': platform.release(),
            },
            'Runtime': {
                'Uptime': str(self.bot.uptime),
                'Start Time': self.bot.start_time,
                'Timezone': time.tzname[1],
            },
            'Network': {
                'Latency': f'{round(self.bot.latency*1000, 2)}ms',
            }
        }

    @group.command(name='shutdown')
    @app_commands.default_permissions(administrator=True)
    @app_commands.check(check_is_owner)
    async def server_shutdown(self, inter:Inter):
        """Shutdown the bot"""
        log.info(
            f'{inter.user.name}#{inter.user.discriminator} '
            f'({inter.user.id}) is shutting down the bot'
        )
        await inter.response.send_message('Shutting down...')
        await self.bot.close()

    @group.command(name='uptime')
    async def server_uptime(self, inter:Inter):
        """Get the uptime of the bot."""

        uptime = str(self.bot.uptime)
        await inter.response.send_message(f'Uptime: {uptime}', ephemeral=True)

    @group.command(name='info')
    async def server_info(self, inter:Inter):
        """Get info on the bot & server."""

        # Get the info/data
        data = self._get_data()      

        # Embed description
        desc = ''

        # Add the data to the description
        for k, v in data.items():
            desc += f'\n--- {k} ---\n'
            for k2, v2 in v.items():
                desc += f'{k2}: {v2}\n'

        # Create and send the embed to the interaction
        embed = discord.Embed(
            title='Server Info',
            colour=discord.Colour.orange(),
            description=f'Here is some info on the bot & server:\n```{desc}```',
            timestamp=inter.created_at
        )
        embed.set_footer(
            text=f'Requested by {inter.user.name}',
            icon_url=inter.user.display_avatar.url
        )
        await inter.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(InfoCog(bot=bot))
