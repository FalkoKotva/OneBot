"""
Cog class for all cogs to inherit from
"""


from discord.ext import commands


class Cog(commands.Cog):
    """
    A cog class that all cogs should inherit from.
    """

    def __init__(self, bot):
        self.bot: commands.Bot = bot
        
    @commands.Cog.listener()
    async def on_ready(self):
        """
        Method called when the cog has been loaded.
        Prints a ready message to the console.
        """
        print(f'Loaded Cog (NAME: {self.__class__.__name__})')
