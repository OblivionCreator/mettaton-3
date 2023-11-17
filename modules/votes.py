import disnake
from disnake.ext import commands
from helpers import character, database, config

db = database.Database()
conf = config.Config()


class Votes(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command()
    @commands.has_role(conf.gamemaster_role)
    async def votes(self, inter: disnake.ApplicationCommandInteraction, character_id: int):
        char = db.get_character_by_id(character_id)

        if not char:
            await inter.send(f"There is no character with ID {character_id}!")
            return

        if char._status != 'Pending':
            await inter.send(f"Character with ID {character_id} is not in the 'Pending' status!")
            return

        votes = db.get_votes(char._character_id)

        if not votes:
            await inter.send(f"There are currently no votes for character ID {character_id}!")
            return

        positive_votes = votes[0]
        negative_votes = votes[1]
        if positive_votes != '':
            positive_votes_score = len(positive_votes.split(','))
        else:
            positive_votes_score = 0
        if negative_votes != '':
            negative_votes_score = len(negative_votes.split(','))
        else:
            negative_votes_score = 0
        character_score = positive_votes_score - negative_votes_score

        embed = disnake.Embed(title=f"Votes for {char.name} (ID {char._character_id})",
                              description=f"Votes: {character_score}", color=0x5050fa)

        pos_str = ''
        for vote in positive_votes.split(','):
            member = await inter.guild.get_or_fetch_member(vote)
            if member:
                pos_str += f'{member.name}\n'

        neg_str = ''
        for vote in negative_votes.split(','):
            member = await inter.guild.get_or_fetch_member(vote)
            if member:
                neg_str += f'{member.name.title()}\n'

        embed.add_field(name=f'{positive_votes_score} Positive Votes', value=pos_str)
        embed.add_field(name=f'{negative_votes_score} Negative Votes', value=neg_str)

        await inter.send(embed=embed)


def setup(bot):
    bot.add_cog(Votes(bot))
