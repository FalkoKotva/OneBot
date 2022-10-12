"""ui for the profile window."""

import json
import logging
import textwrap
from io import BytesIO
import discord
import requests
from PIL import Image, ImageDraw, ImageFont


log = logging.getLogger(__name__)


class ProfileImage:
    """
    Creates a profile card for a discord member
    """

    bytes: BytesIO
    image: Image.Image
    template: Image.Image = Image.open('assets/profile/template.png')

    with open('assets/profile/profile.json', encoding='utf-8') as f:
        data: dict = json.load(f)

    def __init__(self, member:discord.Member):
        self.bytes = BytesIO()
        self.member = member

    async def _get_asset_img(self, asset:discord.Asset, ) -> Image.Image:
        """
        Returns an `Image.Image` object from a `discord.Asset`.
        """

        try:
            im_bytes = BytesIO(await asset.read())
        except AttributeError as err:
            log.error(
                'Failed to get asset image, using default image '\
                'instead. Err: %s', err
            )
            im_bytes = BytesIO(
                requests.get(
                    'https://cdn.discordapp.com/embed/avatars/0.png',
                    timeout=30
                ).content
            )

        return Image.open(im_bytes).convert('RGBA')

    async def _wrap_text(
        self,
        draw:ImageDraw.ImageDraw,
        text:str, pos:tuple[int, int],
        font:ImageFont.ImageFont
    ) -> None:
        """
        Insert text into an image.
        """

        log.debug('calculating text wrap...')

        # calculate wraplength
        margin, offset = pos
        for i, line in enumerate(textwrap.wrap(text, width=15, break_long_words=True)):
            draw.text(
                (margin, offset), line, font=font, fill='white', anchor='mt'
            )
            offset += font.getsize(line)[1]
            log.debug('text lines: %s', i + 1)

        log.debug('text wrap calculated.')

    async def create(self) -> None:
        """
        Creates a profile card image and stores it as a `BytesIO` object.
        It can be accessed after this method via the `bytes` attribute.
        """

        member: discord.Member = self.member
        log.info('Creating profile card for %s', member.name)

        # Avatar is the member's profile picture
        log.debug('Getting avatar...')
        avatar_data = self.data['avatar']
        avatar = await self._get_asset_img(member.display_avatar)
        avatar = avatar.resize((avatar_data['width'], avatar_data['height']))

        # Custom banner
        log.debug('Creating banner...')
        banner_data = self.data['banner']
        banner = Image.new(
            'RGBA', (banner_data['width'], banner_data['height']),
            color=discord.Colour.blurple().to_rgb()
        )

        # Level bar is an alias for exp bar
        log.debug('Creating level bar...')
        bar_data = self.data['levelbar']
        bar_trough = Image.new(
            'RGBA', (bar_data['width'], bar_data['height']),
            color=bar_data['colour']
        )
        im_bar = Image.new(
            'RGBA', (int(bar_data['width']*0.6), bar_data['height']),
            color=discord.Colour.blurple().to_rgb()
        )

        # Paste the images onto the template
        log.debug('Pasting images...')
        final_image = Image.new('RGBA', self.template.size)
        final_image.paste(avatar, (avatar_data['x'], avatar_data['y']), avatar)
        final_image.paste(banner, (banner_data['x'], banner_data['y']), banner)
        final_image.paste(bar_trough, (bar_data['x'], bar_data['y']), bar_trough)
        final_image.paste(im_bar, (bar_data['x'], bar_data['y']), im_bar)
        final_image.paste(self.template, (0, 0), self.template)

        log.debug('Adding text...')

        draw = ImageDraw.Draw(final_image)
        await self._wrap_text(
            draw=draw,
            text=f'@{member.display_name}#{member.discriminator}',
            pos=(150, 225),
            font=ImageFont.truetype(
                'assets/fonts/Gidole-Regular.ttf', 30
            )
        )
        # draw.text(
        #     xy=(265+(banner.width/2), 30+(banner.height/2)),
        #     text='DCG Placeholder Text',
        #     font=ImageFont.truetype('assets/fonts/Gidole-Regular.ttf', 55),
        #     align='center',
        #     anchor='mm',
        # )

        self.image = final_image
        final_image.save(self.bytes, format='png')
        self.bytes.seek(0)
