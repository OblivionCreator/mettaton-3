import disnake
from disnake.ext import commands
from helpers import character, database, config

db = database.Database()
conf = config.Config()


class Delete(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command()
    async def delete(self, inter: disnake.MessageCommandInteraction, character_id:int):

        char = db.get_character_by_id(character_id)

        if not char:
            await inter.send("Character with ID {} was not found!".format(character_id), ephemeral=True)
            return

        if not inter.author.id == char._owner and inter.guild.get_role(conf.gamemaster_role) not in inter.author.roles:
            await inter.send("You do not own this character!", ephemeral=True)
            return

        components = [disnake.ui.Button(label="Yes", style=disnake.ButtonStyle.red, custom_id=f'delete-{character_id}-{inter.author.id}-confirm'), disnake.ui.Button(label="No", style=disnake.ButtonStyle.green, custom_id=f'delete-{character_id}-{inter.author.id}-cancel')]

        await inter.send(f"Are you sure you wish to delete {char.name} (ID: {character_id})?", components=components)

    @commands.Cog.listener("on_button_click")
    async def delete_button_press(self, inter:disnake.MessageInteraction):
        if inter.data.custom_id.startswith('delete-'):
            split_data = inter.data.custom_id.split('-')
            character_id = int(split_data[1])
            owner_id = split_data[2]
            confirm = split_data[3]
            char = db.get_character_by_id(character_id)
            if inter.author.id == char._owner or inter.guild.get_role(conf.gamemaster_role) in inter.author.roles:
                if confirm != 'confirm':
                    await inter.send("Character deletion cancelled.")
                    return
                char = db.get_character_by_id(character_id)
                db.disable_character(character_id)
                await inter.response.edit_message(f"Character {char.name} (ID: {character_id}) has been deleted!", components=[])
            else:
                await inter.send("You do not own this character!", ephemeral=True)
        else:
            return

def setup(bot):
    bot.add_cog(Delete(bot))