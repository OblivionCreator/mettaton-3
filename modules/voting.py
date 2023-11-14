import disnake
from disnake.ext import commands
from helpers import character, database, config

db = database.Database()
conf = config.Config()


class Voting(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command()
    async def approve(self, inter:disnake.ApplicationCommandInteraction):
        self.change_status(self, inter, status='Approved')

    @commands.slash_command()
    async def deny(self, inter:disnake.ApplicationCommandInteraction):
        self.change_status(self, inter, status='Denied')

    @commands.slash_command()
    async def kill(self, inter:disnake.ApplicationCommandInteraction):
        self.change_status(self, inter, status='Dead')

    async def change_status(self, inter, status:str):


def setup(bot):
    bot.add_cog(Voting(bot))
