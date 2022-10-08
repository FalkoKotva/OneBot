"""Cog for info commands."""

import logging
import aiosqlite
import discord
from discord import app_commands, Interaction as Inter
from discord.ext import tasks
from datetime import datetime, time
from num2words import num2words

from cog import BaseCog
from constants import DATABASE


log = logging.getLogger(__name__)


class BirthdayCog(BaseCog, name='Birthdays'):
    """Cog for info commands."""

    def __init__(self, bot):
        super().__init__(bot=bot)
        self.group.guild_ids = (bot.main_guild.id,)
        self.check_birthdays.start()

    @tasks.loop(time=time(hour=7))
    async def check_birthdays(self):
        """Check if it's anyone's birthday, if so send a message."""

        log.debug('Checking birthdays')
        async with aiosqlite.connect(DATABASE) as db:
            data = await db.execute_fetchall(
                """SELECT user_id, birthday FROM user_birthdays"""
            )
        
        if not data:
            log.debug('I don\'t know anyone\'s birthday')

        # Get the current date to check against
        now = datetime.now()

        # Loop through all users
        for user_id, bday_str in data:

            # Convert the string to a datetime object
            bday = datetime.strptime(bday_str, '%d/%m/%Y')

            # If today is not the user's birthday, skip them
            if not (bday.month == now.month and bday.day == now.day):
                continue

            age = now.year - bday.year

            # It's there birthday, celebrate!
            await self.celebrate_birthday(user_id, age)

    async def celebrate_birthday(self, user_id, age):
        """Celebrate a user's birthday.

        Args:
            user_id (int): The user's ID
        """

        # Get the channel to celebrate in
        channel_id = self.bot.config['guild']['channel_ids']['alerts']
        channel = self.bot.get_channel(channel_id)

        member = channel.guild.get_member(user_id)

        # If the member is not in the guild, we can't celebrate
        if not member:
            # TODO: remove user bday from database
            log.debug(
                f'Member ({user_id}) not found, '
                'skipping their birthday'
            )
            return

        ordinal_age = num2words(age, to='ordinal_num')
        user_count = len(channel.guild.members) - 1  # -1 for the user

        desc = f'Happy {ordinal_age} birthday {member.mention}!' \
            '\nCongratulations on another year of life! ' \
            f'All **{user_count}** of us here on the server' \
            ' are wishing you a great day!'

        # Create the embed
        embed = discord.Embed(
            title='Happy Birthday!',
            description=desc,
            colour=member.colour
        )

        # Set the thumbnail to the user's avatar
        embed.set_thumbnail(url=member.display_avatar.url)

        # Send the celebration announcement!
        await channel.send(embed=embed)

    group = app_commands.Group(
        name='birthday',
        description='Birthday commands'
    )

    @group.command(name='celebrate')
    @app_commands.default_permissions(moderate_members=True)
    async def force_celebrate_birthday(
        self,
        inter:Inter,
        member:discord.Member,
        age:int = 0
    ):
        """
        Celebrate a birthday regardless of if it is actually
        their birthday or not.
        """

        await self.celebrate_birthday(member.id, age)
        await inter.response.send_message(
            'Birthday celebrated!',
            ephemeral=True
        )

    @group.command(name='check')
    @app_commands.default_permissions(moderate_members=True)
    async def force_check_birthdays(self, inter:Inter):
        """Force check for birthdays, skipping the daily auto check."""

        await self.check_birthdays()
        await inter.response.send_message('Checked birthdays', ephemeral=True)

    @group.command(name='save')
    async def add_birthday(self, inter:Inter, birthday:str):
        """
        Save your birthday and recieve a happy birthday message
        on your birthday.
        """

        # Convert the string to a datetime object
        try:
            bday = datetime.strptime(birthday, '%d/%m/%Y')
        except ValueError:
            await inter.response.send_message(
                'Invalid date format, please use DD/MM/YYYY',
                ephemeral=True
            )
            return

        now = datetime.now()
        valid_range = range(now.year-40, now.year-12)
        str_range = f'{valid_range.start} & {valid_range.stop-1}'

        # Check that the date range is valid
        if bday.year not in valid_range:
            await inter.response.send_message(
                f'Invalid year, please use a year between {str_range}',
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
    
    @group.command(name='see')
    async def get_birthday(self, inter:Inter):
        """See your birthday if it is saved."""
        
        async with aiosqlite.connect(DATABASE) as db:
            data = await db.execute_fetchall(
                """SELECT birthday FROM user_birthdays WHERE user_id = ?""",
                (inter.user.id,)
            )
        
        if not data:
            await inter.response.send_message(
                'I don\'t know your birthday, sorry!'
                '\nYou can save it with `/birthday save DD/MM/YYYY`',
            )
            return
        
        await inter.response.send_message(f'Your birthday is on {data[0][0]}!')


async def setup(bot):
    await bot.add_cog(BirthdayCog(bot=bot))
