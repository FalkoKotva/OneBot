"""Embeds for the project"""

import logging
from datetime import datetime
import discord
from discord import Interaction as Inter
from tabulate import tabulate
from num2words import num2words

from utils import normalized_name
from constants import BDAY_HELP_MSG


log = logging.getLogger(__name__)


class HelpChannelsEmbed(discord.Embed):
    """Embed to list channels and their descriptions"""

    def __init__(self, channels:list[discord.TextChannel]):

        # A shorthand for the guild
        guild = channels[0].guild

        super().__init__(
            title=f'Help - {guild.name} Channels',
            description='A list of channels and their topics',
            colour=discord.Colour.gold(),
        )

        # Get all of the channels and topics into lists
        channel_names, channel_topics = [], []
        for channel in channels:
            if not isinstance(channel, discord.TextChannel):
                continue

            if len(str(channel.topic)) > 60:
                channel.topic = channel.topic[:56] + ' ...'

            channel_names.append(channel.mention)
            channel_topics.append(channel.topic or '\u200b')

        # Display all of the channel names
        self.add_field(
            name='Channel Name',
            value='\n'.join(channel_names)
        )

        # Display all of the channel topics
        self.add_field(
            name='Channel Topic',
            value='\n'.join(channel_topics)
        )

        # Get the guild icon url for the footer
        url = guild.icon.url if guild.icon else None

        # Add a footer with a help message
        self.set_footer(
            text='Use `/help` to get more help commands',
            icon_url=url
        )


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
            colour=discord.Colour.gold()
        )


class CelebrateBirthdayEmbed(discord.Embed):
    """Embed for celebrating birthdays"""

    def __init__(
        self,
        member:discord.Member,
        age:int,
        member_count:int,
        reactions:tuple
    ):
        ordinal_age = num2words(age, to='ordinal_num')
        text_reactions = ' or '.join(reactions)

        # This is the celebration message
        desc = 'Congratulations on another year of life!' \
               f'\n\nHappy {ordinal_age} birthday {member.mention}!' \
               f'\nAll **{member_count}** of us here on the '  \
                'server are wishing you the greatest of days!' \
               f'\n\nReact with {text_reactions} to celebrate!'

        # Footer text
        f_text = 'Learn about birthdays with `/birthday help`'

        super().__init__(
            title='Happy Birthday!',
            description=desc,
            colour=member.colour
        )

        self.set_thumbnail(url=member.display_avatar.url)
        self.set_footer(text=f_text)


class NextBirthdayEmbed(discord.Embed):
    """Embed for the next persons birthday"""

    def __init__(
        self,
        inter:Inter,
        birthdays:list[tuple[int, datetime]]
    ):

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
