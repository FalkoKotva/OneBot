"""
discord UI kit objects.
"""

import discord
import discord.ui as ui
from discord import Interaction


class ReportModal(ui.Modal, title='Report Ticket'):
    accused = ui.TextInput(
        label='Who are you reporting?',
        placeholder='exampleuser#1234'
    )
    reason = ui.TextInput(
        label='What is the reason for your report?',
        style=discord.TextStyle.long
    )
    
    async def on_submit(self, interaction: Interaction, /) -> None:
        await interaction.response.send_message(
            'Thanks for your report {0.user.mention}!'.format(interaction) /
            'We will look into it as soon as possible.'
        )
