import disnake
from disnake.ext import commands
from helpers import database

db = database.Database()
class View(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(guild_ids=[770428394918641694])
    async def view(self, inter:disnake.ApplicationCommandInteraction, character_id:int):
        view_char = db.get_character_by_id(character_id)

        if not view_char:  # If view_char returns None, there is nothing to show.
            await inter.send(f"There is no character with ID {character_id}!")
            return
        embed, file = view_char.get_character_view()


        # Creates an embed that enables viewing a specific field
        options = []
        options.append("Summary")
        for o in vars(view_char).keys():
            if o == 'misc':
                continue

            o.replace("_", " ")
            options.append(o.title())
        for o in view_char.misc.keys():
            options.append(o.title())

        dropdown = disnake.ui.StringSelect(custom_id=f'fieldview-{character_id}-{inter.author.id}', options=options)


        if file:  # I wish there was a cleaner way to do this check.
            await inter.send(embed=embed, file=file, components=[dropdown])
            return
        await inter.send(embed=embed, components=[dropdown])

    @commands.Cog.listener("on_dropdown")
    async def view_dropdown_listener(self, inter: disnake.MessageInteraction):

        # Makes sure this is a fieldview interaction.
        if not inter.data.custom_id.startswith('fieldview-'):
            return

        split_data = inter.data.custom_id.split('-')

        character_id = int(split_data[1])
        view_char = db.get_character_by_id(character_id)

        if not view_char:  # In case the character gets deleted while the old view remains.
            await inter.send(f"Character with ID {character_id} not found!", ephemeral=True)
            return

        # Checks to make sure interactor is the same person who called /view
        if inter.user.id != int(split_data[2]):
            await inter.send(f"Only the person who called /view can modify the view!", ephemeral=True)
            return

        # Changes the page to be the active page.

        if inter.data.values[0] == "Summary":  # Displays the entire character application
            embed, file = view_char.get_character_view()
            if file:
                await inter.response.edit_message(embed=embed, file=file)
            else:
                await inter.response.edit_message(embed=embed)
        elif inter.data.values[0].lower() in vars(view_char).keys():  # Displays pre-made fields.
            embed = view_char.get_field_view(character_id=character_id, field=inter.data.values[0].lower())
            await inter.response.edit_message(embed=embed)
        elif inter.data.values[0].lower() in view_char.misc.keys():  # Displays misc fields.
            embed = view_char.get_field_view(character_id=character_id, field=inter.data.values[0].lower())
            await inter.response.edit_message(embed=embed)

def setup(bot):
    bot.add_cog(View(bot))