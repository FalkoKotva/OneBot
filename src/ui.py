"""
discord UI kit objects.
"""

import discord
import discord.ui as ui
from discord import Interaction
from typing import Coroutine


class ReportModal(ui.Modal, title='Report Ticket'):
    """
    Modal for users to report other users.
    """
    
    accused = ui.TextInput(
        label='Who are you reporting?',
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
        await interaction.response.send_message(
            'Thanks for your report {0.user.mention}!'.format(interaction) +
            '\nWe will look into it as soon as possible.',
            ephemeral=True
        )
        await self.func(self.accused.value, self.reason.value)


class SuggestionModal(ui.Modal, title='Suggestion Ticket'):
    """
    Modal for users to submit suggestions for the server.
    """
    
    suggestion = ui.TextInput(
        label='What suggestion/feature request would you like to share?',
        style=discord.TextStyle.long
    )
    
    def __init__(self, func: Coroutine):
        super().__init__()
        self.func = lambda *args: func(*args)
    
    async def on_submit(self, interaction: Interaction):
        await interaction.response.send_message(
            'Thanks for your suggestion {0.user.mention}!'.format(interaction) +
            '\nWe will look into it as soon as possible.',
            ephemeral=True
        )
        await self.func(self.suggestion.value)
