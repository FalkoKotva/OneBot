"""
Utils for the project
"""

import discord
from typing import Union


async def get_member(interaction: discord.Interaction, member: str):
    """
    Convert a username or user id into a discord.Member object and return it.
    """

    guild = interaction.guild
    
    # If the member is digits, it's likely a user id
    if member.isdigit():
        return guild.get_member(int(member))

    # Otherwise, it's likely a username, so we'll use that
    return guild.get_member_named(member)
