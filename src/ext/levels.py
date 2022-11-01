"""Level progression cog"""

import logging
from typing import Tuple
from math import sqrt, ceil

import discord
from discord import app_commands
from discord import Interaction as Inter
from discord.ext import commands

from db import db, MemberLevelModel
from ui import LevelCard
from ui.levelcards import ScoreBoard
from utils import is_bot_owner
from exceptions import EmptyQueryResult
from . import BaseCog


log = logging.getLogger(__name__)


class LevelCog(BaseCog, name='Level Progression'):
    """Level progression cog"""

    def __init__(self, bot):
        super().__init__(bot=bot)

        # Create the context menu for the rank cmd
        rank_menu = app_commands.ContextMenu(
            name="Get Rank",
            callback=self.get_levelcard_ctxmenu,
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

    @commands.Cog.listener(name="on_member_remove")
    async def remove_member(self, member:discord.Member):
        """Event to remove members from the rank database"""

        log.debug("Removing member %s", member)

        db.execute(
            "DELETE FROM member_levels WHERE member_id=? AND guild_id=?",
            member.id, member.guild.id
        )

        log.debug("Completed removal")

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

    async def validate_members(self, guild:discord.Guild=None):
        """Iterate through all members in the guild and add them to
        the rank database if they aren't in it.

        Will only validate members in the given guild if one is given.
        """

        log.debug("Validating members")

        guilds = (guild,) or self.bot.guilds

        i = 0
        for guild in guilds:
            for i, member in enumerate(guild.members):
                self.register_member(member)

            log.debug("Validated %s members for %s", i, guild.name)

    @app_commands.command(name="scoreboard")
    async def see_scoreboard(self, inter:Inter, ephemeral:bool=False):
        """Get a scoreboard of the top 5 members by rank"""

        log.debug("Scoreboard command triggered")

        await inter.response.defer(ephemeral=ephemeral)

        members = [
            (
                await self.bot.get.member(member_id, inter.guild.id),
                MemberLevelModel(member_id, inter.guild.id, xp)
            )
            for member_id, xp in db.records(
                "SELECT member_id, experience FROM member_levels "
                "WHERE guild_id=? ORDER BY experience DESC LIMIT 5",
                inter.guild.id
            )
        ]

        scoreboard = ScoreBoard(members)
        await scoreboard.draw()
        await inter.followup.send(file=scoreboard.get_file())

        # # Create the embed
        # embed = discord.Embed(
        #     title="Top 5 members",
        #     description="The top 5 members by rank",
        #     color=discord.Color.blurple()
        # )

        # level_objects = (
        #     MemberLevelModel.from_database(member.id, inter.guild.id)
        #     for member in inter.guild.members[:4] if not member.bot
        # )

        # if not level_objects:
        #     await inter.response.send_message(
        #         "No users to check.",
        #         ephemeral=ephemeral
        #     )
        #     return

        # level_objects = sorted(level_objects, key=lambda x: x.rank)

        # # Add the fields
        # for lvl_obj in level_objects:
        #     member = await self.bot.get.member(lvl_obj.member_id, inter.guild.id)
        #     embed.add_field(
        #         name=f"{lvl_obj.rank}. {member}",
        #         value=f"Level: {lvl_obj.level}\nExp: {lvl_obj.xp}/{lvl_obj.next_xp}",
        #         inline=False
        #     )

        # # Send the embed
        # await inter.response.send_message(embed=embed, ephemeral=ephemeral)

    async def send_levelboard(
        self,
        inter:Inter,
        member:discord.Member | None,
        ephemeral:bool
    ) -> None:
        """Responds to the given interaction with the levelboard"""

        # The interaction member does not have a status
        # which is needed for the level card, so we need
        # to get the member from the guild again.
        member = member or inter.user
        member = await self.bot.get.member(
            member.id, inter.guild.id
        )

        log.debug('%s is checking the rank of %s', inter.user, member)

        await inter.response.defer(ephemeral=ephemeral)

        if member.bot:
            log.debug("Member is a bot, not sending levelboard")
            await inter.followup.send(
                f"Sorry, {member.display_name} is a bot "
                "and can't have a rank!",
                ephemeral=ephemeral
            )
            return

        try:
            # Create the level object from the database
            level_object = MemberLevelModel.from_database(
                member.id, inter.guild.id
            )

        except EmptyQueryResult as err:
            log.error(err)
            await self.register_member(member)
            await inter.followup.send(
                f"I couldn't find {member.mention} in the database."
                "\nI've corrected this now, please try again.",
                ephemeral=True
            )
            return

        # Create the level card
        levelcard = LevelCard(member, level_object)
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
    async def get_levelcard_cmd(
        self,
        inter:Inter,
        member:discord.Member=None,
        ephemeral:bool=False
    ):
        """Get the levelboard of a server member"""

        await self.send_levelboard(inter, member, ephemeral)

    async def get_levelcard_ctxmenu(self, inter:Inter, member:discord.Member):
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
