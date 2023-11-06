import disnake
from disnake.ext import commands

class Template(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command()
    async def temp_func(self, ctx):
        await ctx.send("Hello!", ephemeral=True)

def setup(bot):
    bot.add_cog(Template(bot))
