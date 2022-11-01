"""Database object models"""

import logging
from dataclasses import dataclass
from math import sqrt, ceil

from discord import Member
from discord.ext.commands import Bot

from . import db
from utils import abbreviate_num


log = logging.getLogger(__name__)


@dataclass
class MemberLevelModel:
    """Dataclass to store member level data"""

    member_id: int
    guild_id: int
    xp_raw: int

    def __post_init__(self):
        self.level_raw = 0.07 * sqrt(self.xp_raw)
        self.next_xp_raw = (ceil(self.level_raw) / 0.07) ** 2

        log.debug("Created MemberLevelModel Instance")

    @property
    def xp(self) -> str:
        """Get the member experience points"""

        log.debug("Getting member xp")
        return abbreviate_num(self.xp_raw - 1)

    @property
    def next_xp(self) -> int:
        """Get the member experience points needed for the next level"""

        log.debug("Getting member next xp")
        return abbreviate_num(self.next_xp_raw - 1)

    @property
    def level(self) -> int:
        """Get the member level"""

        log.debug("Getting member level")
        return ceil(self.level_raw)

    @property
    def rank(self) -> int:
        """Get the member rank"""

        log.debug("Getting member rank")
        rank = db.field(
            "SELECT ROW_NUMBER() OVER( ORDER BY experience ) " \
            "FROM member_levels " \
            "WHERE guild_id = ? AND member_id = ?",
            self.guild_id, self.member_id
        )
        if rank is None:
            return "?"

        return rank

    @classmethod
    def from_database(cls, member_id: int, guild_id:int):
        """Create the object from database data"""

        log.debug("Creating MemberLevelModel from database")
        xp = db.field(
            "SELECT experience FROM member_levels " \
            "WHERE member_id = ? AND guild_id = ?",
            member_id, guild_id
        )
        if not xp:
            raise ValueError("No data found for member in guild")

        return cls(member_id, guild_id, xp)

