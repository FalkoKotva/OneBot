"""Views for the bot"""

import logging

import discord
from discord import Interaction as Inter


log = logging.getLogger(__name__)


class EmbedPageView(discord.ui.View):
    """Controls for the embed page view"""

    def __init__(self, multi_embed):
        super().__init__(timeout=None)
        self.multi_embed = multi_embed

    async def _btn_event(self, inter:Inter, page:int):
        """Handle the button press event"""

        log.debug('Button pressed for page: %s', page)

        if page not in range(0, self.multi_embed.pages):
            log.debug('Invalid page: %s', page)
            await self.multi_embed.send(inter)
            return

        log.debug('Moving to page: %s', page)

        self.multi_embed.current_page = page
        await self.multi_embed.send(inter)

    async def update_buttons(self, inter:Inter):
        """Update the buttons"""

        log.debug('Updating buttons')

        self.children[0].disabled = self.on_first_page
        self.children[1].disabled = self.on_last_page

        if inter.response.is_done():
            await inter.edit_original_response(view=self)

    @property
    def on_first_page(self) -> bool:
        """Check if the current page is the first page"""

        return self.multi_embed.current_page == 0

    @property
    def on_last_page(self) -> bool:
        """Check if the current page is the last page"""

        return self.multi_embed.current_page \
            == self.multi_embed.pages - 1

    @discord.ui.button(
        label='Prev Page',
        style=discord.ButtonStyle.secondary,
        custom_id='prev_page',
    )
    async def prev_page(self, inter:Inter, _):
        """When the next page button has been pressed"""

        await self._btn_event(inter, self.multi_embed.current_page - 1)

    @discord.ui.button(
        label='Next Page',
        style=discord.ButtonStyle.primary,
        custom_id='next_page',
    )
    async def next_page(self, inter:Inter, _):
        """When the next page button has been pressed"""

        await self._btn_event(inter, self.multi_embed.current_page + 1)

    @discord.ui.button(
        label='Delete',
        style=discord.ButtonStyle.danger,
        custom_id='delete'
    )
    async def delete(self, inter:Inter, _):
        """When the delete button has been pressed"""

        await self.multi_embed.delete()
