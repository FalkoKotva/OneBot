"""ui modals"""

import logging
from typing import Callable
from datetime import datetime
import discord
from discord import Interaction as Inter
from discord import ui as dui


log = logging.getLogger(__name__)


class BirthdayModal(dui.Modal, title='Birthday'):
    """Modal for submitting member birthdays"""

    birthday_input = dui.TextInput(
        label='Please enter your birthday!',
        placeholder='DD/MM/YYYY',
        style=discord.TextStyle.short
    )

    def __init__(self, save_func:Callable):
        super().__init__()
        self._save_func = save_func

    async def on_submit(self, inter:Inter):  # pylint: disable=arguments-differ

        # Get the entered birthday
        value = self.birthday_input.value
        bday = datetime.strptime(value, "%d/%m/%Y")

        # Get the validation range
        now = datetime.now()
        valid_range = range(now.year-40, now.year-12)

        # Check that the birthday date range is valid
        if bday.year not in valid_range:
            raise OverflowError()

        self._save_func(value)

        await inter.response.send_message(
            'I\'ve saved your special date, '
            'I can\'t wait to wish you a happy birthday!',
            ephemeral=True
        )

    async def on_error(self, inter:Inter, error):  # pylint: disable=arguments-differ

        if isinstance(error, ValueError):
            msg = 'Invalid date format. Please try again.'

        elif isinstance(error, OverflowError):
            msg = 'Date is too far into the past or present.' \
                'Please try again.'

        else:
            msg = f'An unknown issue occured. Contact an admin.' \
                f'\nError: {error}'

        await inter.response.send_message(
            content=msg,
            ephemeral=True
        )
