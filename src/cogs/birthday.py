"""Cog for info commands."""

import asyncio
import logging
import schedule
import aiosqlite
from discord import app_commands, Interaction as Inter
from datetime import datetime

from cog import BaseCog
from constants import DATABASE


log = logging.getLogger(__name__)


class BirthdayCog(BaseCog, name='Birthdays'):
    """Cog for info commands."""

    def __init__(self, bot):
        super().__init__(bot=bot)
        self.group.guild_ids = (bot.main_guild.id,)
        # schedule.every().day.at("21:25").do(lambda: asyncio.run(self.check_birthdays()))

    async def check_birthdays(self):
        print('something')
        
    async def daily_task(self):
        while True:
            schedule.run_pending()
            print('something first')
            asyncio.sleep(1)

    # @commands.Cog.listener()
    # async def on_ready(self):
    #     self.bot.loop.create_task(self.daily_task())

    group = app_commands.Group(
        name='birthday',
        description='Birthday commands'
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
