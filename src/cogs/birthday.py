"""Cog for info commands."""

import logging
import aiosqlite
import discord
from discord import app_commands, Interaction as Inter
from datetime import datetime

from cog import Cog
from constants import DATABASE, GUILD_ID


log = logging.getLogger(__name__)


class BirthdayCog(Cog, name='Birthdays'):
    """Cog for info commands."""

    def __init__(self, bot):
        super().__init__(bot=bot)

    group = app_commands.Group(
        name='birthday',
        description='Birthday commands',
        guild_ids=(GUILD_ID,),
    )

    @group.command(name='save')
    async def add_birthday(self, inter:Inter, birthday:str):
        """Save your birthday and recieve a happy birthday message on your birthday."""
        
        try:
            datetime.strptime(birthday, '%d/%m/%Y')
        except ValueError:
            await inter.response.send_message(
                'Invalid date format, please use DD/MM/YYYY',
                ephemeral=True
            )
            return
    
        async with aiosqlite.connect(DATABASE) as db:
            try:
                await db.execute(
                    """INSERT INTO user_birthdays (user_id, birthday) VALUES (?, ?)""",
                    (inter.user.id, birthday)
                )
                await db.commit()
            except aiosqlite.IntegrityError:
                await inter.response.send_message(
                    'You already have a birthday set',
                    ephemeral=True
                )
                return
        
        await inter.response.send_message(
            'I\'ve saved your special date, I can\'t wait to wish you a happy birthday!',
            ephemeral=True
        )
    
    @group.command(name='forget')
    async def remove_birthday(self, inter:Inter):
        """Remove your birthday from the database."""
        
        async with aiosqlite.connect(DATABASE) as db:
            await db.execute(
                """DELETE FROM user_birthdays WHERE user_id = ?""",
                (inter.user.id,)
            )
            await db.commit()
        
        await inter.response.send_message(
            'If I knew it, I\'ve forgotten your birthday!',
            ephemeral=True
        )


async def setup(bot):
    await bot.add_cog(BirthdayCog(bot=bot))
