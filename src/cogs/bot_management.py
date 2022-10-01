"""Bot cog to manage important features of the bot"""

import os
from discord import app_commands, Interaction as Inter
from discord.ext import commands

from constants import GUILD_ID, ADMIN_ROLE_ID


def cogs_choices() -> list[str]:
    return [
        app_commands.Choice(name=fn[:-3], value=fn)
        for fn in os.listdir('./src/cogs')
        if fn.endswith('.py') and not fn.startswith('__')
    ]

async def check_perms(inter:Inter) -> bool:
    """"""
    admin_role = inter.guild.get_role(ADMIN_ROLE_ID)
    return admin_role in inter.user.roles


class BotManagement(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        
    cogs_group = app_commands.Group(
        name='cog',
        description='Cog commands...',
        guild_ids=(GUILD_ID,)
    )
    
    @cogs_group.command(name='load')
    @app_commands.check(check_perms)
    @app_commands.choices(cogs=cogs_choices())
    async def load_cog(self, inter:Inter, cogs:app_commands.Choice[str]):
        """Load a cog"""
        
        await self.bot.load_extension(f'cogs.{cogs.name}')
        await inter.response.send_message(f'loaded cog {cogs.name}')
    
    @cogs_group.command(name='unload')
    @app_commands.check(check_perms)
    @app_commands.choices(cogs=cogs_choices())
    async def unload_cog(self, inter:Inter, cogs:app_commands.Choice[str]):
        """Unload a cog"""
        
        await self.bot.unload_extension(f'cogs.{cogs.name}') 
        await inter.response.send_message(f'unloaded cog {cogs.name}')
    
    @cogs_group.command(name='reload')
    @app_commands.check(check_perms)
    @app_commands.choices(cogs=cogs_choices())
    async def reload_cog(self, inter:Inter, cogs:app_commands.Choice[str]):
        """Reload a cog"""
        
        await self.bot.unload_extension(f'cogs.{cogs.name}')
        await self.bot.load_extension(f'cogs.{cogs.name}')
        await inter.response.send_message(f'reloaded cog {cogs.name}')


async def setup(bot):
    await bot.add_cog(BotManagement(bot))
