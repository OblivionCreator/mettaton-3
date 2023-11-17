import disnake
from disnake.ext import commands
from helpers import character, database, config

db = database.Database()
conf = config.Config()


class Set(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command()
    async def set(self, inter:disnake.ApplicationCommandInteraction, character_id:int, field:str, value:str):

        char = db.get_character_by_id(character_id)


        if not char:
            await inter.send("Character with ID {} was not found!".format(character_id), ephemeral=True)
            return

        if not inter.author.id == char._owner and inter.guild.get_role(conf.gamemaster_role) not in inter.author.roles:
            await inter.send("You do not own this character!", ephemeral=True)
            return

        embed = disnake.Embed()

        if field.lower() in vars(char).keys():

            if value.lower().strip() == 'delete':
                await inter.send("You can not delete this field!", ephemeral=True)
                return

            setattr(char, field.lower(), value)
            db.update_character(char)

            embed.title = f"Field {field} has been changed."
            embed.description = value
            await inter.send(embed=embed)
        else:
            # field does not exist, add to custom roles.
            # deletes existing fields.
            if value.lower().strip() == 'delete':
                for key in char.misc.keys():
                    if key.lower() == field.lower():
                        char.misc.pop(key)
                        db.update_character(char)
                        await inter.send(f"Custom Field {field} has been deleted.")
                        return
            success = False

            # add new field

            embed.title = f"Field {field} has been changed."
            embed.description = value

            for key in char.misc.keys():
                if key.lower() == field.lower():
                    char.misc[key] = value
                    success = True
                    break

            if not success:
                char.misc[field] = value
                db.update_character(char)

            await inter.send(embed=embed, ephemeral=True)


def setup(bot):
    bot.add_cog(Set(bot))
