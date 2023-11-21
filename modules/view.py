import io

import disnake
from disnake.ext import commands
from helpers import database

db = database.Database()
class View(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(description='Shorthand for /view')
    async def cm(self, inter:disnake.ApplicationCommandInteraction, character_id:int):
        await self.view(inter, character_id)
        # i only did this because i'd never hear the end of it otherwise.


    @commands.slash_command(description='View a specific character by ID.')
    async def view(self, inter:disnake.ApplicationCommandInteraction, character_id:int):
        view_char = db.get_character_by_id(character_id)

        if not view_char:  # If view_char returns None, there is nothing to show.
            await inter.send(f"There is no character with ID {character_id}!")
            return
        embed = view_char.get_character_view(guild=inter.guild)

        # Creates an embed that enables viewing a specific field
        options = []
        dump_to_file = False
        options.append("Summary")
        for o in vars(view_char).keys():
            if len(str(vars(view_char)[o])) >= 1024:
                dump_to_file = True
            # Does not add immutable fields to the list as they're always kinda the same.
            # Does not add 'misc' to the list as this is just JSON.
            # Does not add empty fields to the list
            if o == 'misc' or o.startswith('_') or vars(view_char)[o] is None or vars(view_char)[o] == '' or vars(view_char)[o] == 'None':
                continue
            options.append(o.title())
        for o in view_char.misc.keys():
            if len(view_char.misc[o]) >= 1024:
                dump_to_file = True
            options.append(o)

        dropdown = disnake.ui.StringSelect(custom_id=f'fieldview-{character_id}-{inter.author.id}', options=options)

        if dump_to_file:
            # Adds a file attachment to the view as well.

            filecontent = ''

            for o in vars(view_char).keys():
                if o == 'misc' or vars(view_char)[o] is None or vars(view_char)[o] == '' or vars(view_char)[o] == 'None':
                    continue
                filecontent += f'{o.strip("_").replace("_", " ").title()}: {vars(view_char)[o]}\n'
            for o in view_char.misc.keys():
                filecontent += f'{o.title()}: {view_char.misc[o]}\n'

            bb = io.BytesIO(filecontent.encode("utf-8"))
            file = disnake.File(bb)
            file.filename = f'character_{character_id}.txt'
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
            embed = view_char.get_character_view(guild=inter.guild)
            await inter.edit_original_message   .edit_message(embed=embed)
        elif inter.data.values[0].lower() in vars(view_char).keys():  # Displays pre-made fields.
            embed = view_char.get_field_view(character_id=character_id, field=inter.data.values[0].lower())
            await inter.response.edit_message(embed=embed)
        elif inter.data.values[0] in view_char.misc.keys():  # Displays misc fields.
            embed = view_char.get_field_view(character_id=character_id, field=inter.data.values[0])
            await inter.response.edit_message(embed=embed)

def setup(bot):
    bot.add_cog(View(bot))