"""Extension for user settings"""

import sqlite3
import logging

from discord import (
    app_commands,
    Interaction as Inter
)

from db import db
from . import BaseCog


log = logging.getLogger(__name__)

settings = [
    app_commands.Choice(name=name, value=_id)
    for _id, name in db.records(
        "SELECT id, name FROM settings"
    )
]

class SettingsCog(BaseCog, name="User Settings"):
    """Cog for user settings"""

    group = app_commands.Group(
        name="settings",
        description="User settings"
    )

    @group.command(name="set")
    @app_commands.choices(setting=settings)
    async def set_setting_cmd(
        self,
        inter:Inter,
        setting:app_commands.Choice[int],
        choice:bool
    ):
        """Set the value of one of your settings.

        Args:
            inter (Inter): the app command interaction
            setting (app_commands[int]): The setting you wish to change
            choice (bool): The value of the setting
        """

        log.debug(
            "A user is changing their settings"
            "\n%s - %s", setting.name, choice
        )

        try:
            db.execute(
                "INSERT INTO user_settings "
                "(user_id, setting_id, value) "
                "VALUES (?, ?, ?)",
                inter.user.id,
                setting.value,
                choice
            )

        except sqlite3.IntegrityError:
            log.debug("Updating existing setting")
            db.execute(
                "UPDATE user_settings SET value=? "
                "WHERE user_id=? AND setting_id=?",
                choice,
                inter.user.id,
                setting.value
            )

        await inter.response.send_message(
            f"{setting.name} set to {choice}",
            ephemeral=True
        )

    @group.command(name="see")
    async def see_settings_cmd(self, inter:Inter):
        """See your current settings"""

        log.debug("A user is seeing their settings")
        settings = db.records(
            "SELECT name, value FROM user_settings "
            "JOIN settings ON user_settings.setting_id = settings.id "
            "WHERE user_id = ?",
            inter.user.id
        )

        print(settings)

        if not settings:
            await inter.response.send_message(
                "**You have no settings**",
                ephemeral=True
            )
            return

        msg = "**Your Settings:**\n\n"
        for setting in settings:
            msg += f"{setting[0]}: {bool(setting[1])}\n"

        await inter.response.send_message(msg, ephemeral=True)


async def setup(bot):
    """Setup the cog"""

    await bot.add_cog(SettingsCog(bot))
