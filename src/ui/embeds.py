"""Embeds for the project"""

import logging
from datetime import datetime
import discord
from discord import Interaction as Inter
from tabulate import tabulate

from utils import normalized_name
from constants import BDAY_HELP_MSG


log = logging.getLogger(__name__)


class BirthdayHelpEmbed(discord.Embed):
    """Embed for listing birthday commands"""

    def __init__(self, inter:Inter, app_commands:list):

        # Create a table of the commands
        desc = tabulate(
            [
                # /command - description
                (f'/{cmd.qualified_name}', cmd.description)
                for cmd in app_commands
            ],
            headers=('Command', 'Description')
        )

        # Initialize the embed
        super().__init__(
            title='Help - Birthday Commands',
            description=f'```{desc}```',
            colour=discord.Colour.dark_gold()
        )


class NextBirthdayEmbed(discord.Embed):
    """Embed for the next persons birthday"""

    def __init__(self, inter:Inter, birthdays:list[tuple[int, datetime]]):

        log.debug('Creating new NextBirthdayEmbed')

        now = datetime.now()

        for member_id, birthday in birthdays:

            # If their birthday has not past, break
            birthday = birthday.replace(year=now.year)
            if not birthday < now:
                break

        else:  #nobreak
            # The next birthday is next year
            member_id, birthday = birthdays[0]
            birthday = birthday.replace(now.year + 1)

        # Get the member object
        member = inter.guild.get_member(member_id)

        # Get the unix timestamp for the birthday
        unix = int(birthday.timestamp())

        log.debug(
            'Found Birthday: %s unix_timestamp: %s',
            normalized_name(member), unix
        )

        # Set the title and description
        title = 'Next Birthday'
        desc = f'Next birthday will be for {member.mention} on '\
               f'<t:{unix}:D> which is <t:{unix}:R>'

        log.debug('Initializing NextBirthdayEmbed')

        # Initialize the embed
        super().__init__(
            title=title,
            description=desc,
            colour=member.colour
        )

        self.set_thumbnail(url=member.display_avatar.url)
        self.set_footer(text=BDAY_HELP_MSG)
