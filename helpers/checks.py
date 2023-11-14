import disnake
from disnake.ext import commands
from helpers import character, database, config


def check_for_gamemaster_role(self, ctx: commands.Context):
    for i in ctx.author.roles:
        if i.id == config.gamemaster_role:
            return True
    return False
