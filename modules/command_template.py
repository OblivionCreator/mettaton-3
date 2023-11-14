import disnake
from disnake.ext import commands
from helpers import character, database, config

db = database.Database()
conf = config.Config()


class Template(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command()
    async def template(self, ctx):
        pass


def setup(bot):
    bot.add_cog(Template(bot))
