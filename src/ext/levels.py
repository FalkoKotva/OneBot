"""Level progression cog"""

import logging
from typing import Tuple
from math import sqrt, ceil

import discord
from discord import app_commands
from discord import Interaction as Inter
from discord.ext import commands

from db import db
from ui import LevelCard
from utils import is_bot_owner
from . import BaseCog


log = logging.getLogger(__name__)


class LevelCog(BaseCog, name='Level Progression'):
    """Level progression cog"""

    def __init__(self, bot):
        super().__init__(bot=bot)

        # Create the context menu for the rank cmd
        rank_menu = app_commands.ContextMenu(
            name="Get Rank",
            callback=self.context_see_member_levelboard,
        )
        self.bot.tree.add_command(rank_menu)

    @commands.Cog.listener()
    async def on_ready(self):
        """Event to validate the database when cog is ready"""

        await self.bot.wait_until_ready()
        await self.validate_members()

    @commands.Cog.listener(name="on_member_join")
    async def register_new_member(self, member:discord.Member):
        """Event to add new members to the rank database"""
        self.register_member(member)

    def calc_level(self, exp:float) -> float:
        """Calculate the level from the given exp"""

        return 0.07 * sqrt(exp)

    def calc_exp(self, level:float) -> float:
        """Calculate the exp for the given level"""

        return (level / 0.07) ** 2

    def calc_next_exp(self, level:float) -> float:
        """Calculate the next level exp from the given level"""

        return (ceil(level) / 0.07) ** 2

    async def get_level_for(
        self, member:discord.Member, guild_id:int
    ) -> Tuple[float, float, float, int]:
        """Get level data for the given member

        Args:
            member (discord.Member): _description_

        Returns:
            Tuple[float, float, float, int]: The lvl data for the member
        """

        # Get their data from the database
        data = db.records(
            "SELECT * FROM member_levels WHERE guild_id=?",
            guild_id
        )

        # We can't continue if there is no data
        if not data:
            return

        # Order the data by exp
        data = sorted(data, key=lambda x: x[-1], reverse=True)

        # Find the rank of the member
        for rank, record in enumerate(data):
            if record[1] == member.id:
                break

        # pylint: disable=undefined-loop-variable
        # ^ False-positive: if there is no data we return early

        # Get the level data
        exp = record[-1]
        level = self.calc_level(exp)
        next_exp = self.calc_next_exp(level)

        return (
            level + 1,  # Otherwise lvl calculation is 1 behind
            exp - 1,  # Otherwise exp calculation is 1 ahead
            next_exp - 1,  # Otherwise next_exp calculation is 1 ahead
            rank + 1  # Otherwise rank calculation is 1 behind
        )

    async def gain_exp(self, member:discord.Member, amount:int):
        """Gives the given member the given amount of exp"""

        log.info(
            '%s from %s is gaining %s exp',
            member, member.guild.name, amount
        )

        # Get their data from the database
        db_exp = db.field(
            "SELECT experience FROM member_levels WHERE member_id=? AND guild_id=?",
            member.id, member.guild.id
        )

        # We can't continue if they aren't in the database.
        if not db_exp:
            log.info(
                '%s is not in the database, cant update their level',
                member
            )
            return

        exp = db_exp + amount

        db.execute(
            "UPDATE member_levels SET experience = ? " \
            "WHERE member_id=? AND guild_id=?",
            exp, member.id, member.guild.id
        )

        log.info('Updated exp for %s to %s', member, exp)

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

        await self.gain_exp(message.author, 35)

    @commands.Cog.listener()
    async def on_member_update(self, _, member:discord.Member):
        """On member update event

        Args:
            _ (discord.Member): The member before the update
            member (discord.Member): The member after the update
        """

        log.debug("Member update event triggered by %s", member)

        if member.bot:
            log.debug("Member is a bot, ignoring")
            return

        await self.gain_exp(member, 150)

    def register_member(self, member:discord.Member):
        """Register a new member in the database

        Args:
            member (discord.Member): The member to register
        """

        log.debug("Registering new member %s", member)

        if member.bot:
            log.debug("Member is a bot, not registering")
            return

        # Check if they are already in the database
        exists = db.records(
            "SELECT * FROM member_levels WHERE member_id=? AND guild_id=?",
            member.id, member.guild.id
        )
        if exists:
            log.debug(
                "Member is already in the database with this guild, " \
                "not registering"
            )
            return

        db.execute(
            "INSERT INTO member_levels(member_id, guild_id) VALUES(?, ?)",
            member.id, member.guild.id
        )

        log.debug("Completed registration")

    async def validate_members(self):
        """Iterate through all members in the guild and add them to
        the rank database if they aren't in it"""

        log.debug("Validating members")

        i = 0
        for guild in self.bot.guilds:
            for i, member in enumerate(guild.members):
                self.register_member(member)

            log.debug("Validated %s members for %s", i, guild.name)

    @app_commands.command(name="scoreboard")
    async def see_scoreboard(self, inter:Inter):
        """Get a scoreboard of the top 5 members by rank"""

        log.debug("Scoreboard command triggered")

        # Create the embed
        embed = discord.Embed(
            title="Top 5 members",
            description="The top 5 members by rank",
            color=discord.Color.blurple()
        )

        data = [
            (member.id,) + await self.get_level_for(member, inter.guild.id) \
            for member in inter.guild.members
        ]

        if not data:
            await inter.response.send_message(
                "No users to check.",
                ephemeral=True
            )
            return

        data = sorted(data, key=lambda x: x[-1])

        # Add the fields
        for member_id, level, exp, next_exp, rank in data[:5]:
            member = await self.bot.get.member(member_id)
            embed.add_field(
                name=f"{rank}. {member}",
                value=f"Level: {level}\nExp: {exp}/{next_exp}",
                inline=False
            )

        # Send the embed
        await inter.response.send_message(embed=embed)

    async def send_levelboard(
        self,
        inter:Inter,
        member:discord.Member,
        ephemeral:bool
    ) -> None:
        """Responds to the given interaction with the levelboard"""

        log.debug('%s is checking the rank of %s', inter.user, member)

        await inter.response.defer(ephemeral=ephemeral)

        if member.bot:
            log.debug("Member is a bot, not sending levelboard")
            await inter.followup.send(
                f"Sorry, {member.display_name} is a bot and can't have a rank!",
                ephemeral=ephemeral
            )
            return

        # Get the level data for the member
        level_data = await self.get_level_for(member, inter.guild.id)

        # We can't continue if there is no data
        if not level_data:
            await inter.followup.send(
                "Your levels are not being tracked, " \
                "contact an administrator",
                ephemeral=True
            )
            return

        # Unpack the level data
        level, exp, next_exp, rank = level_data

        # We need to get the member again because the member object
        # provided by the app command does not contain the member's
        # status, which we need to draw the card.
        guild = await self.bot.get.guild(inter.guild.id)
        member = guild.get_member(member.id)

        # Create the level card
        levelcard = LevelCard(
            member=member,
            level=int(level),
            exp=int(exp),
            next_exp=int(next_exp),
            rank=rank,
            is_darkmode=True
        )

        # Draw the card
        await levelcard.draw()

        # All done! Send the card as a file.
        await inter.followup.send(
            file=levelcard.get_file(),
            ephemeral=ephemeral
        )

    @app_commands.command(name='rank')
    @app_commands.describe(
        member="The member to see the rank of",
        ephemeral="Hide the bot response from other users"
    )
    async def see_member_levelboard(
        self,
        inter:Inter,
        member:discord.Member=None,
        ephemeral:bool=False
    ):
        """Get the levelboard of a server member"""

        # Default to the command author if no member is given
        member = member or inter.user
        await self.send_levelboard(inter, member, ephemeral)

    async def context_see_member_levelboard(self, inter:Inter, member:discord.Member):
        """Context menu version of see_member_levelboard"""

        await self.send_levelboard(inter, member, ephemeral=True)

    # Admin only commands belong to this group
    admin_group = app_commands.Group(
        name='rank-admin',
        description='Admin commands for the rank system',
        default_permissions=discord.Permissions(moderate_members=True)
    )

    @admin_group.command(name="validate-members")
    async def force_validate_members(self, inter:Inter):
        """Force validate all members in the guild"""

        await self.validate_members()

        await inter.response.send_message(
            "Validation Complete!",
            ephemeral=True
        )

    @admin_group.command(name="add-xp")
    @app_commands.check(is_bot_owner)
    async def add_xp_cmd(self, inter:Inter, target:discord.Member, xp:int):
        """Add xp to a member, only the bot owner can use this"""

        await self.gain_exp(target, xp)

        await inter.response.send_message(
            f"Added {xp} xp to {target.mention}",
        )


async def setup(bot):
    """Setup function for the cog"""

    cog = LevelCog(bot)
    await bot.add_cog(cog)
