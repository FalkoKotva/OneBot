"""Embeds for the project"""

import logging
import discord
from discord import Interaction as Inter
from datetime import datetime

from constants import DATE_FORMAT
from utils import normalized_name


log = logging.getLogger(__name__)


class NextBirthdayEmbed(discord.Embed):
    """Embed for the next persons birthday"""

    def __init__(self, inter:Inter, birthdays:list[tuple[int, datetime]]):

        log.debug('Creating NextBirthdayEmbed')        

        now = datetime.now()

        for member_id, birthday in birthdays:

            # If their birthday has not past, break
            birthday = birthday.replace(year=now.year)
            if not birthday < now:
                break
        
        else:
            # The next birthday is next year
            member_id, birthday = birthdays[0]
            birthday = birthday.replace(now.year + 1)

        member = inter.guild.get_member(member_id)
        bday_str = birthday.strftime(DATE_FORMAT)
        days_until = (birthday - now).days
        
        log.debug(
            f'Birthday found: {normalized_name(member)} \
                {birthday=} {days_until=}'
        )

        title = 'Next Birthday'
        desc = 'Next birthday will be for {} on {} which is in {} days' \
            .format(member.mention, bday_str, days_until)

        log.debug('Initializing NextBirthdayEmbed')

        # Initialize the embed
        super().__init__(
            title=title,
            description=desc,
            colour=member.colour,
            timestamp=inter.created_at
        )
