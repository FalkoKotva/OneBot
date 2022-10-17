"""Level progression cog"""

import logging
import sqlite3
from typing import Tuple
from math import sqrt, ceil

import discord
from discord import app_commands
from discord import Interaction as Inter
from discord.ext import commands

from db import db
from ui import get_levelboard
from . import BaseCog


log = logging.getLogger(__name__)


class LevelCog(BaseCog, name='Level Progression'):
    """Level progression cog"""

    async def get_level_for(
        self, member:discord.Member
    ) -> Tuple[float, float, float, int]:
        """Get level data for the given member

        Args:
            member (discord.Member): _description_

        Returns:
            Tuple[float, float, float, int]: The lvl data for the member
        """

        # Get their data from the database
        data = db.records("SELECT * FROM member_levels")

        # We can't continue if there is no data
        if not data:
            return

        data = sorted(data, key=lambda x: x[2], reverse=True)
        for rank, record in enumerate(data):
            if record[0] == member.id:
                break

        # Get the exp
        _, _, exp = record  # pylint: disable=undefined-loop-variable
        # Calculate the current level
        level = 0.07 * sqrt(exp)
        log.debug('Calculated level for %s to be %s', member, level)

        # Calculate the next level exp
        next_exp = (ceil(level) / 0.07) ** 2
        log.debug('Calculated next level exp for %s to be %s', member, next_exp)

        return level, exp, next_exp, rank + 1  # # pylint: disable=undefined-loop-variable

    async def gain_exp(self, member:discord.Member, amount:int):
        """Gives the given member the given amount of exp"""

        log.debug('%s is gaining %s exp', member, amount)

        # Get their data from the database
        data = db.record(
            "SELECT * FROM member_levels WHERE member_id = ?",
            member.id
        )

        # We can't continue if they aren't in the database.
        if not data:
            log.debug(
                '%s is not in the database, cant update their level',
                member
            )
            return

        exp = data[2] + amount

        db.execute(
            "UPDATE member_levels SET experience = ? " \
            "WHERE member_id = ?",
            exp, member.id
        )
        db.commit()

        log.debug('Updated exp for %s to %s', member, exp)

        return exp

    @commands.Cog.listener()
    async def on_message(self, message:discord.Message):
        """On message event.

        Args:
            message (discord.Message): The discord msg object
        """

        log.debug("Message event triggered by %s", message.author)

        if message.author.bot:
            log.debug("Message author is a bot, ignoring")
            return

        await self.gain_exp(message.author, 20)

    @commands.Cog.listener(name="on_member_join")
    async def register_new_member(self, member:discord.Member):
        """Register a new member in the database

        Args:
            member (discord.Member): The member to register
        """

        log.debug("Registering new member %s", member)

        if member.bot:
            log.debug("Member is a bot, not registering")
            return

        try:
            db.execute(
                "INSERT INTO member_levels(member_id, guild_id) VALUES(?, ?)",
                member.id, member.guild.id
            )
            db.commit()
        except sqlite3.IntegrityError:
            log.debug("Member %s is already in the database", member)
            return

        log.debug("Completed registration")

    admin_group = app_commands.Group(
        name='rank-admin',
        description='Admin commands for the rank system'
    )

    @admin_group.command(name="validate-members")
    async def validate_members(self, inter:Inter):
        """Validate that all of the guild members are in the ranking
        database.
        """

        for member in inter.guild.members:
            await self.register_new_member(member)

        await inter.response.send_message(
            "Validation Complete!",
            ephemeral=True
        )

    group = app_commands.Group(
        name='rank',
        description='Commands for the rank system',
    )

    @group.command(name='see')
    @app_commands.describe(
        member="The member to see the rank of",
        ephemeral="Hide the bot response from other users"
    )
    @app_commands.describe(member="The member to see the level of")
    async def see_member_levelboard(
        self,
        inter:Inter,
        member:discord.Member=None,
        ephemeral:bool=False
    ):
        """Get your current levelboard"""

        member = member or inter.user

        log.debug('%s is checking the rank of %s', inter.user, member)

        data = await self.get_level_for(member)
        if not data:
            await inter.response.send_message(
                "Your levels are not being tracked, " \
                "contact an administrator",
                ephemeral=True
            )
            return

        level, exp, next_exp, rank = data

        # Get the levelboard
        levelboard = await get_levelboard(
            member, int(level), int(exp), int(next_exp), rank
        )
        await inter.response.send_message(
            file=levelboard,
            ephemeral=ephemeral
        )
        levelboard.close()

async def setup(bot):
    """Setup function for the cog"""

    cog = LevelCog(bot)
    await bot.add_cog(cog)
