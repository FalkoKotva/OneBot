"""
discord UI kit objects.
"""

import logging
import textwrap
import requests
import discord
import discord.ui as ui
from discord import Interaction
from typing import Coroutine
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

from constants import AVATAR_SIZE, BANNER_SIZE


log = logging.getLogger(__name__)


class LevelObject:
    exp: int
    exp_next: int
    level: int
    rank: int
    
    def __init__(self, member:discord.Member):
        self.exp = 0
        self.exp_next = 0
        self.level = 0
        self.rank = 0


class ProfileImage:
    """
    Creates a profile card for a discord member
    """

    bytes: BytesIO
    image: Image.Image

    def __init__(self, member:discord.Member):
        self.bytes = BytesIO()
        self.member = member

    async def _get_asset_img(self, asset:discord.Asset, ) -> Image.Image:
        """
        Returns an `Image.Image` object from a `discord.Asset`.
        """

        try:
            bytes = BytesIO(await asset.read())
        except AttributeError as err:
            log.error(
                f'Failed to get asset image, using default image \
                    instead. Err: {err}'
            )
            bytes = BytesIO(
                requests.get(
                    'https://cdn.discordapp.com/embed/avatars/0.png'
                ).content
            )

        return Image.open(bytes).convert('RGBA')

    async def _add_text(self, draw:ImageDraw.ImageDraw, text:str, pos:tuple[int, int], align:tuple[str, str]) -> None:
        """
        Insert text into an image.
        """

        log.debug('calculating text wrap...')
        font = ImageFont.truetype('assets/fonts/Gidole-Regular.ttf', 30)

        # calculate wraplength
        margin, offset = pos
        for i, line in enumerate(textwrap.wrap(text, width=15, break_long_words=True)):
            draw.text(
                (margin, offset), line, font=font, fill='white', anchor='mt'
            )
            offset += font.getsize(line)[1]
            log.debug(f'text lines: {i+1}')
        
        log.debug('text wrap calculated.')

    async def create(self) -> None:
        """
        Creates a profile card image and stores it as a `BytesIO` object.
        It can be accessed after this method via the `bytes` attribute.
        """

        member: discord.Member = self.member

        log.info(f'Creating profile card for {member.name}')

        # The template is the card itself without the pictures or text
        template = Image.open('assets/profile_template.png')

        log.debug('Getting avatar...')

        # Avatar is the member's profile picture
        avatar = await self._get_asset_img(member.display_avatar)
        avatar = avatar.resize(AVATAR_SIZE)

        # log.debug('Getting banner...')

        # # Banner is the member's profile banner
        # banner = await self._get_asset_img(member.banner)
        # banner = banner.resize(BANNER_SIZE)

        log.debug('Pasting images...')

        # Paste the images onto the template
        final_image = Image.new('RGBA', template.size)
        final_image.paste(avatar, (75, 50), avatar)
        # final_image.paste(banner, (), banner)
        final_image.paste(template, (0, 0), template)
        
        log.debug('Adding text...')
        
        draw = ImageDraw.Draw(final_image)
        await self._add_text(
            draw=draw,
            text=f'@{member.display_name}#{member.discriminator}',
            pos=(150, 225),
            align=('center', 'mm')
        )

        self.image = final_image
        final_image.save(self.bytes, format='png')
        self.bytes.seek(0)


class ReportModal(ui.Modal, title='Report Ticket'):
    """
    Modal for users to report other users.
    """

    accused = ui.TextInput(
        label='Who would you like to report?',
        placeholder='exampleuser#1234'
    )
    reason = ui.TextInput(
        label='What is the reason for your report?',
        style=discord.TextStyle.long
    )
    
    def __init__(self, func: Coroutine):
        super().__init__()
        self.func = lambda *args: func(*args)

    async def on_submit(self, interaction: Interaction):
    
        #
        await self.func(interaction, self.accused.value, self.reason.value)
    
        # Send a message to confirm the report
        await interaction.response.send_message(
            'Thanks for your report {0.user.mention}!'.format(interaction) +
            '\nWe will look into it as soon as possible.',
            ephemeral=True
        )


class SuggestionModal(ui.Modal, title='Suggestion Ticket'):
    """
    Modal for users to submit suggestions for the server.
    """
    
    suggestion = ui.TextInput(
        label='What suggestion would you like to share?',
        style=discord.TextStyle.long
    )
    
    def __init__(self, func: Coroutine):
        super().__init__()
        self.func = lambda *args: func(*args)
    
    async def on_submit(self, interaction: Interaction):
        await self.func(interaction, self.suggestion.value)

