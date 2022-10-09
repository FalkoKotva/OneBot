"""ui modals"""

import logging
import discord
from discord import ui, Interaction
from typing import Coroutine


log = logging.getLogger(__name__)


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
