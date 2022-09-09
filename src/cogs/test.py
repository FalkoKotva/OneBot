"""
Test Cog file
"""

from discord.ext import commands
from cog import Cog


class Test(Cog):
    """
    Test Cog.
    """

    def __init__(self, bot):
        super().__init__(bot)
        
    @commands.command(name='test')
    async def test(self, ctx):
        """
        Test command.
        """
        await ctx.send('I am alive!')


async def setup(bot):
    """
    Setup function.
    Required for all cog files.
    Used by the bot to load this cog.
    """

    cog = Test(bot)
    await bot.add_cog(cog)
