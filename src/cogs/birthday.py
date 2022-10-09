"""Cog for the automated birthday celebration system."""

import logging
import aiosqlite
import discord
from discord import app_commands, Interaction as Inter
from discord.ext import tasks
from datetime import datetime, time
from num2words import num2words
from functools import cache

from cog import BaseCog
from constants import DATABASE
from utils import normalized_name


log = logging.getLogger(__name__)


class BirthdayCog(BaseCog, name='Birthdays'):
    """Cog for info commands."""

    def __init__(self, bot):
        super().__init__(bot=bot)

        # Start the task to check for birthdays
        self.check_birthdays.start()

    @tasks.loop(time=time(hour=7))
    async def check_birthdays(self):
        """Check if it's anyone's birthday, if so send a message."""

        log.debug('Doing daily birthday check')

        # Get all of the birthdays including the user id
        async with aiosqlite.connect(DATABASE) as db:
            data = await db.execute_fetchall(
                """SELECT user_id, birthday FROM user_birthdays"""
            )

        # If there are no birthdays, we can stop here
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
                await self.wrap_up_birthday(user_id)
                continue

            # Calculate the user's age
            age = now.year - bday.year

            # It's there birthday, celebrate!
            await self.celebrate_birthday(user_id, age)

    @cache
    async def celebrate_birthday(self, user_id, age):
        """Celebrate a user's birthday.

        Args:
            user_id (int): The user's ID.
            age (int): The user's age.
        """

        # Get the channel to celebrate in
        channel_id = self.bot.config['guild']['channel_ids']['alerts']
        channel = self.bot.get_channel(channel_id)

        # Get the birthday role
        role_id = self.bot.config['guild']['role_ids']['birthday']
        role = channel.guild.get_role(role_id)

        # Get the user
        member = channel.guild.get_member(user_id)

        # If the member is not in the guild, we can't celebrate
        if not member:
            # TODO: remove user bday from database
            log.debug(
                f'Member ({user_id}) not found, '
                'skipping their birthday'
            )
            return

        # Assign the birthday role to the member
        await member.add_roles(role)

        # Ordinalise the age
        ordinal_age = num2words(age, to='ordinal_num')

        # Number of members in the guild
        user_count = len(channel.guild.members) - 1  # -1 for the user

        # This is the celebration message
        desc = f'Happy {ordinal_age} birthday {member.mention}!' \
            '\nCongratulations on another year of life! ' \
            f'All **{user_count}** of us here on the server' \
            ' are wishing you a great day!'

        # This embed contains the celebration message
        embed = discord.Embed(
            title='Happy Birthday!',
            description=desc,
            colour=member.colour
        )

        # Set the thumbnail to the user's avatar
        embed.set_thumbnail(url=member.display_avatar.url)

        # Send the celebration announcement!
        await channel.send(embed=embed)

    async def wrap_up_birthday(self, user_id:int):
        """Stop celebrating a user birthday

        Args:
            user_id (int): The user's ID.
        """

        log.debug('Attempting to wrap up birthday')

        # Get the guild
        guild_id = self.bot.main_guild_id
        guild = self.bot.get_guild(guild_id)

        # Get the birthday role
        role_id = self.bot.config['guild']['role_ids']['birthday']
        role = guild.get_role(role_id)

        # Get the user
        member = guild.get_member(user_id)
        name = normalized_name(member)

        # Remove the role from the member
        if role in member.roles:
            log.info(f'Removing birthday role from {name}')
            await member.remove_roles(role)
            return

        log.debug(
            'Birthday role not found, '
            f'skipping {name}'
        )


    # All birthday commands are in this group
    group = app_commands.Group(
        name='birthday',
        description='Birthday commands'
    )

    @group.command(name='list')
    @app_commands.default_permissions(moderate_members=True)
    async def list_birthdays(self, inter:Inter):
        """Returns list of members and their birthdays."""

        # Get all birthdays from the database with the user's id
        async with aiosqlite.connect(DATABASE) as db:
            data = await db.execute_fetchall(
                "SELECT user_id, birthday FROM user_birthdays"
            )

        # Return if no birthdays are set
        if not data:
            inter.response.send_message(
                'There are no birthdays in the database.',
                ephemeral=True
            )
            return

        # Get list of members and their birthdays
        bday_list = [
            f'{inter.guild.get_member(uid).mention}: {bday}'
            for uid, bday in data
        ]

        # Put the list into a string and send it
        await inter.response.send_message(
            '\n'.join(bday_list),
            ephemeral=True
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

        # Just call the normal celebrate function
        await self.celebrate_birthday(member.id, age)

        # Respond to the interaction to avoid an error
        await inter.response.send_message(
            'Birthday celebrated!',
            ephemeral=True
        )

    @group.command(name='wrapup')
    @app_commands.default_permissions(moderate_members=True)
    async def force_wrap_up_birthday(
        self,
        inter:Inter,
        member:discord.Member
    ):
        """Stop celebrating a birthday."""

        # Just call the normal wrap up function
        await self.wrap_up_birthday(member.id)

        # Respond to the interaction to avoid an error
        await inter.response.send_message(
            'Birthday wrapped up!',
            ephemeral=True
        )

    @group.command(name='check')
    @app_commands.default_permissions(moderate_members=True)
    async def force_check_birthdays(self, inter:Inter):
        """Force check for birthdays, skipping the daily auto check."""

        # Just call the normal check task function
        await self.check_birthdays()

        # Respond to the interaction to avoid an error
        await inter.response.send_message(
            'Checked birthdays!',
            ephemeral=True
        )

    @group.command(name='save')
    async def add_birthday(self, inter:Inter, birthday:str):
        """
        Save your birthday and recieve a happy birthday message
        on your birthday.
        """

        # Convert the string to a datetime object
        # ValueError will be raised if it's not a valid format
        try:
            bday = datetime.strptime(birthday, '%d/%m/%Y')
        except ValueError:
            await inter.response.send_message(
                'Invalid date format, please use DD/MM/YYYY',
                ephemeral=True
            )
            return

        # Get the validation range for the entered birthday date
        now = datetime.now()
        valid_range = range(now.year-40, now.year-12)
        str_range = f'{valid_range.start} & {valid_range.stop-1}'

        # Check that the birthday date range is valid
        if bday.year not in valid_range:
            await inter.response.send_message(
                f'Invalid year, please use a year between {str_range}',
                ephemeral=True
            )
            return

        # Save the birthday to the database
        async with aiosqlite.connect(DATABASE) as db:
            try:
                await db.execute(
                    """INSERT INTO user_birthdays (user_id, birthday)
                    VALUES (?, ?)""",
                    (inter.user.id, birthday)
                )

                # Commit the changes
                await db.commit()
   
            # Raised if the user already has a birthday saved
            # (user id unique constraint failed)
            except aiosqlite.IntegrityError:
                await inter.response.send_message(
                    'You already have a birthday set',
                    ephemeral=True
                )
                return

        log.info(
            f'Birthday saved for {inter.user.display_name} '
            f'at {birthday}'
        )

        await inter.response.send_message(
            'I\'ve saved your special date, ' /
            'I can\'t wait to wish you a happy birthday!',
            ephemeral=True
        )

    @group.command(name='forget')
    async def remove_birthday(self, inter:Inter):
        """Remove your birthday from the database."""

        # Delete the birthday from the database
        async with aiosqlite.connect(DATABASE) as db:
            await db.execute(
                """DELETE FROM user_birthdays WHERE user_id = ?""",
                (inter.user.id,)
            )

            # Commit the changes
            await db.commit()

        log.info(f'Birthday removed for {inter.user.display_name}')

        # Let the user know their birthday has been removed
        await inter.response.send_message(
            'If I knew it, I\'ve forgotten your birthday!',
            ephemeral=True
        )

    @group.command(name='see')
    async def get_birthday(self, inter:Inter):
        """See your birthday if it is saved."""

        # Get the birthday from the database that matches the member id
        async with aiosqlite.connect(DATABASE) as db:
            data = await db.execute_fetchall(
                "SELECT birthday FROM user_birthdays WHERE user_id = ?",
                (inter.user.id,)
            )

        # If the user doesn't have a birthday saved
        if not data:
            await inter.response.send_message(
                'I don\'t know your birthday, sorry!'
                '\nYou can save it with `/birthday save DD/MM/YYYY`',
            )
            return

        # Inform the user of their saved birthday
        await inter.response.send_message(
            f'Your birthday is on {data[0][0]}!'
        )


async def setup(bot):
    """Extension setup function"""

    cog = BirthdayCog(bot)
    await bot.add_cog(cog)
