"""Embeds for the project"""

import logging
from datetime import datetime
import discord
from discord import Interaction as Inter

from constants import DATE_FORMAT
from utils import normalized_name


log = logging.getLogger(__name__)


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
        # Cast the birthday to a formatted string
        bday_str = birthday.strftime(DATE_FORMAT)
        # Get the number of days until the next birthday
        days_until = (birthday - now).days

        log.debug(
            'Found Birthday: %s birthday = %s, days until = %s',
            normalized_name(member), birthday, days_until
        )

        # Set the title and description
        title = 'Next Birthday'
        desc = f'Next birthday will be for {member.mention} on'\
            f'{bday_str} which is in {days_until} days'

        log.debug('Initializing NextBirthdayEmbed')

        # Initialize the embed
        super().__init__(
            title=title,
            description=desc,
            colour=member.colour,
            timestamp=inter.created_at
        )
