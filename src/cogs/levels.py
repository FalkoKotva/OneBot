"""Level progression cog"""

from math import sqrt, ceil
import logging
import sqlite3

import discord
from discord import app_commands
from discord import Interaction as Inter
from easy_pil import Editor, Canvas, load_image_async, Font

from db import db
from utils import normalized_name
from . import BaseCog


log = logging.getLogger(__name__)


class LevelCog(BaseCog, name='Level Progression'):
    """Level progression cog"""

    async def get_levelboard(self, member:discord.Member, level:int, exp:int, next_exp:int):
        """Returns a levelboard for the given member"""

        accent = member.colour.to_rgb()

        background = Editor(Canvas((900, 210), color="#141414"))
        background.rounded_corners(10)
        avatar_img = await load_image_async(member.avatar.url)
        avatar_outline = Editor(Canvas((170, 170), color="#141414")).circle_image()
        avatar = Editor(avatar_img).resize((150, 150)).circle_image()

        poppins = Font.poppins(size=40)
        poppins_small = Font.poppins(size=30)

        background.polygon(
            ((50, 0), (0, 50), (90, 90), (180, 0)),
            fill=accent,
        )
        background.polygon(
            ((0, 50), (50, 0), (90, 90), (0, 180)),
            fill=accent,
        )
        background.rectangle((0, 0), width=100, height=100, fill=accent, radius=10)
        background.paste(avatar_outline, (20, 20))
        background.paste(avatar, (30, 30))

        background.rectangle((210, 140), width=660, height=40, color="#2F2F2F", radius=20)
        background.bar(
            (210, 140), max_width=660, height=40, color=accent,
            radius=20, percentage=(exp / next_exp) * 100
        )
        background.text(
            (210, 90), normalized_name(member, False), font=poppins, color="#F5F5F5"
        )

        background.text(
            (870, 40),
            text=f"LEVEL {level}",
            font=poppins,
            color=accent,
            align="right"
        )
        background.text(
            (870, 90),
            f"{exp} / {next_exp} XP",
            font=poppins_small,
            color="#F5F5F5",
            align='right'
        )

        return discord.File(fp=background.image_bytes, filename="levelboard.png")

    async def get_rank_for(self, member:discord.Member):

        # Get their data from the database
        data = db.record(
            "SELECT * FROM member_levels WHERE member_id = ?",
            member.id
        )

        # We can't continue if they aren't in the database.
        if not data:
            return

        # Get the exp
        _, exp = data

        # Calculate the current level
        level = 0.07 * sqrt(exp)
        log.debug('Calculated level for %s to be %s', member, level)

        # Calculate the next level exp
        next_exp = (ceil(level) / 0.07) ** 2
        log.debug('Calculated next level exp for %s to be %s', member, next_exp)

        levelboard = await self.get_levelboard(member, level, exp, next_exp)
        return levelboard, level, exp, next_exp

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

        exp = data[1] + amount

        db.execute(
            "UPDATE member_levels SET experience = ? " \
            "WHERE member_id = ?",
            exp, member.id
        )

        log.debug('Updated exp for %s to %s', member, exp)

        return exp

    group = app_commands.Group(
        name='rank',
        description='Level progression commands',
    )

    @group.command(name='addexp')
    async def setexp(self, inter:Inter, member:discord.Member, exp:int):
        """Sets the given member's experience"""

        new_exp = await self.gain_exp(member, exp)
        await inter.response.send_message(
            f"Your exp has been updated to {new_exp}",
            ephemeral=True
        )

    @group.command(name='track')
    async def add_to_db(self, inter:Inter, member:discord.Member):
        """Adds the member to the database"""

        log.debug('Adding %s to database', member)

        try:
            db.execute(
                "INSERT INTO member_levels VALUES (?, ?)",
                member.id, 1
            )
            db.commit()
        except sqlite3.IntegrityError as err:
            print(err)
            await inter.response.send_message(
                'Their levels are already being tracked',
                ephemeral=True
            )
            return

        await inter.response.send_message(
            "Their levels are now being tracked!\n" \
            "You can check your level with `/rank member`",
            ephemeral=True
        )

    @group.command(name='untrack')
    async def remove_from_db(self, inter:Inter, member:discord.Member):
        """Removes the member from the database"""

        log.debug('Removing %s from database', member)

        db.execute(
            "DELETE FROM member_levels WHERE member_id = ?",
            member.id
        )
        db.commit()

        await inter.response.send_message(
            "Their levels are no longer being tracked!",
            ephemeral=True
        )

    @group.command(name='me')
    async def get_own_levelboard(self, inter:Inter):
        """Get your current rank"""

        log.debug('%s is checking their rank', inter.user)

        data = await self.get_rank_for(inter.user)
        if not data:
            await inter.response.send_message(
                "Your levels are not being tracked, " \
                "use `/rank track` to start tracking them",
                ephemeral=True
            )
            return

        levelboard, level, exp, next_exp = data

        # Get the levelboard
        levelboard = await self.get_levelboard(inter.user, int(level), int(exp), int(next_exp))
        await inter.response.send_message(
            file=levelboard,
            ephemeral=True
        )
        levelboard.close()

    @group.command(name='member')
    async def get_other_levelboard(self, inter:Inter, member:discord.Member):
        """Get another member's rank"""

        log.debug('%s is checking their rank', member)

        data = await self.get_rank_for(member)
        if not data:
            await inter.response.send_message(
                "Their levels are not being tracked",
                ephemeral=True
            )
            return

        levelboard, level, exp, next_exp = data

        # Get the levelboard
        levelboard = await self.get_levelboard(member, int(level), int(exp), int(next_exp))
        await inter.response.send_message(
            file=levelboard,
            ephemeral=True
        )
        levelboard.close()

async def setup(bot):
    """Setup function for the cog"""

    cog = LevelCog(bot)
    await bot.add_cog(cog)
