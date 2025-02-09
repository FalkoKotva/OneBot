"""Embeds for the project"""

import logging
from datetime import datetime

import discord
from discord import Interaction as Inter
from tabulate import tabulate
from num2words import num2words

from db import db
from utils import normalized_name
from constants import (BDAY_HELP_MSG, PRONOUNDB_LOGIN_URL, PRONOUNDB_SET_URL)
from .views import EmbedPageView


log = logging.getLogger(__name__)



class WelcomeEmbed(discord.Embed):
    """Welcome embed"""

    def __init__(self, member:discord.Member):

        super().__init__(
            title="Welcome to the server!",
            description=f"Thanks for joining {member.mention}"
                "\nPlease read the rules and have fun!",
            colour=discord.Colour.gold(),
            timestamp = datetime.utcnow()
        )
        self.set_thumbnail(url=member.display_avatar.url)
        self.set_footer(text="User joined")


class RemoveEmbed(discord.Embed):
    """Remove embed"""

    def __init__(self, member:discord.Member):

        super().__init__(
            title="Goodbye, you won't be missed!",
            description=f"{member} has left the server."
                "\nAllow me to reach for my tiny violin.",
            colour=discord.Colour.gold(),
            timestamp = datetime.utcnow()
        )
        self.set_thumbnail(url=member.display_avatar.url)
        self.set_footer(text="User left")


class ListMutedEmbed(discord.Embed):
    """List all muted members for the given data"""

    def __init__(self, bot, guild_id:int, data:list):
        super().__init__(
            title="Muted Members",
            description="```{}```",
            colour=discord.Colour.dark_grey()
        )
        self.data = data
        self.guild_id = guild_id

    def _remove_member(self, member_id: int):
        db.execute(
            "DELETE FROM guild_muted WHERE member_id = ? AND guild_id = ?",
            member_id, self.guild_id
        )

    async def populate(self):
        """Populate the embed with the data"""

        desc = ""

        for member_id, reason, end_dt, in self.data:
            member = await self.bot.get.member(member_id, self.guild_id)
            if not member:
                self._remove_member(member_id)
                continue

            desc += f"{member.mention} - {reason} - {end_dt}"

        self.description.format(desc)


class HelpGetPronounsEmbed(discord.Embed):
    """Embed for explaining how to get a member's pronouns"""

    def __init__(self):
        super().__init__(
            title="How to get someone's pronouns",
            colour=discord.Colour.red()
        )

        log.debug("Creating GetPronounsEmbed")

        self.description = \
            "To get someones's pronouns, you need to:" \
            "\n\n**1.** Use the following command\n*`/pronouns get`*" \
            "\n\n**2.** Mention the user you want to get the " \
            "the pronouns for\n*(e.g. `/pronouns get @xord`)*" \
            "\n\n**3.** All done, I will respond with that " \
            "person's pronouns!"


class HelpSetPronounsEmbed(discord.Embed):
    """Embed for explaining how to set your pronouns with PronounDB"""

    def __init__(self):
        super().__init__(
            title="How to set your pronouns",
            colour=discord.Colour.red()
        )

        log.debug("Creating SetPronounsEmbed")

        self.description = \
            "To set your pronouns, you need to:" \
            "\n\n**1.** Go to PronounDB and add your discord account" \
            "\n*You can do this by [clicking here]" \
            f"({PRONOUNDB_LOGIN_URL})*" \
            "\n\n**2.** Set your pronouns on the next page" \
            "\n*If you can't find that, [click here]" \
            f"({PRONOUNDB_SET_URL})*" \
            "\n\n**3.** You're set, well done!" \
            "\n*You can now use `/pronouns get` in the server to " \
            "see your pronouns*"



class ListConfiguredChannelsEmbed(discord.Embed):
    """List all configured channels for this guild"""

    def __init__(self, bot, data:list[tuple[int, int, int]]):

        super().__init__(
            title="Integrated Channels",
            description="List of all channels configured for this guild",
            colour=discord.Colour.blurple()  # cspell: disable-line
        )

        purposes = db.records("SELECT * FROM guild_channel_purposes")
        purpose_map = {id: name for id, name in purposes}

        for channel_id, _, purpose_id in data:
            channel = bot.get_channel(channel_id)

            self.add_field(
                name=purpose_map[purpose_id],
                value=channel.mention,
            )


class SetChannelEmbed(discord.Embed):
    """Embed for setting a channel."""

    def __init__(
        self,
        channel:discord.TextChannel | discord.VoiceChannel,
        key_name: str
    ):
        super().__init__(
            title="Channel Set",
            description=f"Set {channel.mention} to {key_name}",
            timestamp=datetime.utcnow(),
            colour=discord.Colour.green()
        )
        self.set_footer(text="Channel Set")


class ClaimedExpClusterEmbed(discord.Embed):
    """Embed for when a user claims an exp cluster"""

    def __init__(self, member:discord.Member, amount:int):
        super().__init__(
            title='XP Cluster - Claimed!',
            description=f'{member.mention} claimed a cluster of {amount} XP!',
            color=discord.Color.green()
        )


class ExpClusterEmbed(discord.Embed):
    """Embed for EXP clusters"""

    def __init__(self, amount:int):

        super().__init__(
            title='An XP Cluster has appeared!',
            description=f'Hurry, press the claim button to recieve {amount} XP!',
            color=discord.Color.gold()
        )


class EmbedPageManager:
    """An object to manage multiple embeds in a single message"""

    # The last interaction that sent the message
    _last_inter: Inter = None

    # A list of embeds under this manager, each embed is a page
    _embeds = []

    # Properties
    current_page = 0

    @property
    def pages(self):
        """Get the number of embeds in this manager

        Returns:
            int: The number of embeds
        """

        return len(self._embeds)

    def add_embed(self, embed:discord.Embed):
        """Add an embed to the message

        Args:
            embed (discord.Embed): The embed to add
        """

        # Add the page number to the description of the embed
        embed.description += f'\n\n**Page {self.pages + 1}**'

        # Now we can save the embed
        self._embeds.append(embed)

    def add_embeds(self, *embeds):
        """Add multiple embeds to the message

        Args:
            *embeds (discord.Embed): The embeds to add
        """

        log.debug('Adding %s embeds', len(embeds))

        # Just add them as we would a single embed
        for embed in embeds:
            self.add_embed(embed)

    def get_embed(self, index:int):
        """Get an embed from the message

        Args:
            index (int): The index of the embed
        """

        log.debug('Getting embed at index: %s', index)
        return self._embeds[index]

    async def delete(self):
        """Delete the message"""

        await self._last_inter.delete_original_response()

    async def send(self, inter:Inter):
        """Send the message

        Args:
            inter (Inter): The interaction to send the message to
        """

        # Delete the last page, if it exists
        if self._last_inter:
            await self._last_inter.delete_original_response()

        # Create the user controls
        view = EmbedPageView(self)
        await view.update_buttons(inter)

        # Send the new page
        await inter.response.send_message(
            embed=self.get_embed(self.current_page),
            ephemeral=False,  # IMPORTANT
            view=view
        )

        # Save the interaction so we can delete it later if the
        # member changes page
        self._last_inter = inter


class HelpChannelsEmbed(discord.Embed):
    """Embed to list channels and their descriptions"""

    def __init__(self, channels:list[discord.TextChannel]):

        log.debug('Initializing %s', self.__class__.__name__)

        # A shorthand for the guild
        guild = channels[0].guild

        super().__init__(
            title=f'Help - {guild.name} Channels',
            description='A list of channels and their topics',
            colour=discord.Colour.gold(),
        )

        # Sometimes the channels list may be a different type
        channels = list(channels)

        # Do not go any further if there are no channels
        if not channels:
            log.warning('No channels found, returning early')
            return

        log.debug('Formatting channels')

        # We need the names/topics for separate columns
        channel_names, channel_topics = [], []

        for channel in channels:

            # We only want to show text channels
            if not isinstance(channel, discord.TextChannel):
                raise ValueError(f'Invalid channel type: {type(channel)}')

            topic_limit = 55 - len(channel.mention)

            # Prevent really long topics from breaking the embed
            if len(str(channel.topic)) > topic_limit:
                channel.topic = channel.topic[:topic_limit-3] + '...'

            # Add the channel name and topic to the columns
            channel_names.append(channel.mention)
            channel_topics.append(channel.topic or '\u200b')

        log.debug('Formatted %s channels', len(channel_names))

        # The column sizes must match to display the embed correctly
        assert len(channel_names) == len(channel_topics)

        log.debug('Adding fields')

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

        log.debug('Adding footer')

        # Get the guild icon url for the footer
        url = guild.icon.url if guild.icon else None

        # Add a footer with a help message
        self.set_footer(
            text='Use `/help` to get more help commands',
            icon_url=url
        )

        log.debug('Initialized %s', self.__class__.__name__)


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
