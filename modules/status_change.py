import disnake
from disnake.ext import commands
from helpers import character, database, config

db = database.Database()
conf = config.Config()


class Voting(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command()
    @commands.has_role(conf.gamemaster_role)
    async def approve(self, inter: disnake.ApplicationCommandInteraction, character_id: int, reason: str = None):
        await self.change_status(inter, status='Approved', character_id=character_id, reason=reason)

    @commands.slash_command()
    @commands.has_role(conf.gamemaster_role)
    async def deny(self, inter: disnake.ApplicationCommandInteraction, character_id: int, reason: str = None):
        await self.change_status(inter, status='Denied', character_id=character_id, reason=reason)

    @commands.slash_command()
    @commands.has_role(conf.gamemaster_role)
    async def bp(self, inter: disnake.ApplicationCommandInteraction, character_id: int):
        await self.change_status(inter, status='Denied', character_id=character_id, reason=conf.boilerplate)

    @commands.slash_command()
    @commands.has_role(conf.gamemaster_role)
    async def pending(self, inter: disnake.ApplicationCommandInteraction, character_id: int, reason: str = None):
        await self.change_status(inter, status='Pending', character_id=character_id, reason=reason)

    @commands.slash_command()
    @commands.has_role(conf.gamemaster_role)
    async def kill(self, inter: disnake.ApplicationCommandInteraction, character_id: int, reason: str = None):
        await self.change_status(inter, status='Dead', character_id=character_id, reason=reason)

    async def change_status(self, inter: disnake.ApplicationCommandInteraction, status: str, character_id: int,
                            reason: str | None):
        success = db.update_character_status(character_id=character_id, status=status)
        if not success:
            await inter.send(f"Character ID {character_id} does not exist.")
            return
        await inter.send(f"Changed status of character ID {character_id} to {status}")
        character = db.get_character_by_id(character_id=character_id)
        # DMs the owner with the status + reason
        owner = await inter.guild.get_or_fetch_member(character._owner)

        if not reason:
            reason = "No reason provided."

        # let's set some colours depending on status


        if status == 'Approved':
            colour = 0x00ff00
            role = inter.guild.get_role(conf.roleplayer_role)
            if role and owner:
                await owner.add_roles(role)
        elif status == 'Denied':
            colour = 0xff0000
        else:
            colour = 0x000000

        embed = disnake.Embed(title=f"Character ID {character_id} has been set to {status}", description=reason, colour=colour)
        try:
            await owner.send(embed=embed)
        except:
            await inter.send(f"Couldn't send DM to owner of character ID {character_id}")

def setup(bot):
    bot.add_cog(Voting(bot))
