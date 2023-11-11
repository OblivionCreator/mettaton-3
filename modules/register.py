import disnake
from disnake.ext import commands
from helpers import character, database, config

db = database.Database()
conf = config.Config()
class Register(commands.Cog):

    characters: dict

    def __init__(self, bot):
        self.bot = bot
        self.characters = {}

    @commands.slash_command()
    async def register(self, inter: disnake.ApplicationCommandInteraction, character_id: int | None = None):
        new_character = db.get_or_create_character(author_id=inter.author.id, character_id=character_id)
        embed, file = new_character.get_character_view()

        # Sets character status to 'Registering'
        new_character.status = "Registering"
        db.update_character_status(new_character.character_id, new_character.status)

        # Returns if the character is owned by someone else.
        if int(new_character.owner) != inter.author.id:
            await inter.send(f"Someone already has a character with ID {new_character.character_id}!", ephemeral=True)
            return

        # Gets the register channel.
        register_channel = self.bot.get_channel(conf.register_channel)

        # Creates a private thread for this character registration.
        thread = await register_channel.create_thread(name=f"Registration for Character ID {new_character.character_id}", type=disnake.ChannelType.private_thread)

        # Adds the new character registration to the instance.
        self.characters[new_character.character_id] = [thread, new_character]

        # Creates a dropdown menu for this registration

        options = []
        for o in vars(new_character).keys():
            if o == 'misc':
                continue

            o.replace("_", " ")
            options.append(o.title())
        for o in new_character.misc.keys():
            options.append(o.title())

        field_dropdown = disnake.ui.StringSelect(placeholder="Select a field to edit", options=options, custom_id=f'register-{new_character.character_id}-{inter.author.id}')

        # Sends the registration view to the thread.
        if file:
            await thread.send(inter.author.mention, embed=embed, file=file, components=[field_dropdown])
        else:
            await thread.send(inter.author.mention, embed=embed, components=[field_dropdown])
        await inter.send(f"Character registration has been started in {thread.mention}")

    @commands.Cog.listener("on_dropdown")
    async def dropdown_listener(self, inter: disnake.MessageInteraction):
        print("hi!")
        if not inter.data.custom_id.startswith('register'):
            return

        split_data = inter.data.custom_id.split('-')

        character_id = int(split_data[1])
        character = db.get_character_by_id(character_id)

        if not character:
            await inter.send("The character wasn't found! Has it been deleted..?", ephemeral=True)
            return

        if inter.author.id != int(split_data[2]):
            await inter.send("Only the person who called /register can modify the registration!", ephemeral=True)
            return

        value = getattr(character, inter.data.values[0].lower())

        modal_components = disnake.ui.TextInput(label=inter.data.values[0], value=value, required=True, style=disnake.TextInputStyle.long, custom_id=inter.data.values[0].lower())
        await inter.response.send_modal(title=f'Registration for Character ID {character_id}', custom_id=f'rmodal-{character_id}-{inter.author.id}', components=modal_components)

    @commands.Cog.listener("on_modal_submit")
    async def register_modal(self, inter:disnake.MessageInteraction):
        if not inter.data.custom_id.startswith('rmodal'):
            return

        split_data = inter.data.custom_id.split('-')
        temp, character_id, author_id = split_data
        character = db.get_character_by_id(int(character_id))
        if not character:
            await inter.send("The character wasn't found! Has it been deleted..?", ephemeral=True)
            return
        if inter.author.id != int(author_id):
            await inter.send("Only the person who called /register can modify the registration!", ephemeral=True)
            return

        setattr(character, list(inter.text_values)[0], inter.text_values[list(inter.text_values)[0]])

        db.update_character(character)
        embed, file = character.get_character_view()
        if file:
            await inter.response.edit_message(embed=embed, file=file)
        else:
            await inter.response.edit_message(embed=embed)
def setup(bot):
    bot.add_cog(Register(bot))