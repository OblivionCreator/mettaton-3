import disnake
from disnake.ext import commands
from helpers import character, database, config

db = database.Database()
conf = config.Config()

field_options = commands.option_enum({
    "Name": "name",
    "Owner": "owner",
    "ID": "ID",
    "Status": "status",
    "Age": "age",
    "Gender": "gender",
    "Species": "species",
    "Abilities": "abilities",
    "Appearance": "appearance",
    "Backstory": "backstory",
    "Personality": "personality",
    "Prefilled Application": "prefilled",
    "Custom Field": "misc",
    "All Fields": "all fields"
})


class Search(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def build_string(self, inter: disnake.ApplicationCommandInteraction | disnake.MessageInteraction | disnake.ModalInteraction, char_list: list, page: int, field: str,
                     value: str):
        if page < 1:
            page = 1

        if page > len(char_list) / 25 + 1:
            page = int(len(char_list) / 25 + 1)

        search_str = ''

        if len(char_list) == 0:
            return search_str, []

        search_str = '\n'

        for i in range(25 * (page - 1), 25 * page):
            owner = inter.guild.get_member(char_list[i][1])
            owner_str = f"({owner})"
            if not owner:
                owner_str = ""
            search_str += f"**`{char_list[i][0]}`** | {char_list[i][2]} {owner_str}\n"

            if i >= len(char_list) - 1:
                break

        page_total = int(len(char_list) / 25) + 1

        # building the buttons
        # buttons are disabled if at the limit page limit

        multi_left_button = disnake.ui.Button(label="<<", style=disnake.ButtonStyle.green,
                                              custom_id=f'search-{inter.author.id}-{page}-superleft-{field}-{value}')
        one_left_button = disnake.ui.Button(label="<️", style=disnake.ButtonStyle.blurple,
                                            custom_id=f'search-{inter.author.id}-{page}-left-{field}-{value}')
        page_display_button = disnake.ui.Button(label=f"{page} / {page_total}", style=disnake.ButtonStyle.grey,
                                                custom_id=f'search-{inter.author.id}-{page}-select-{field}-{value}')
        right_button = disnake.ui.Button(label=">️", style=disnake.ButtonStyle.blurple,
                                         custom_id=f'search-{inter.author.id}-{page}-right-{field}-{value}')
        multi_right_button = disnake.ui.Button(label=">>", style=disnake.ButtonStyle.green,
                                               custom_id=f'search-{inter.author.id}-{page}-superright-{field}-{value}')

        if page == 1:
            multi_left_button.disabled = True
            one_left_button.disabled = True
        if page == page_total:
            multi_right_button.disabled = True
            right_button.disabled = True

        components = [multi_left_button, one_left_button, page_display_button, right_button, multi_right_button]
        return search_str, components


    # Search Command
    @commands.slash_command()
    async def search(self, inter: disnake.ApplicationCommandInteraction, field: field_options, value: str):
        value = value.strip()

        if value.startswith('<@') and field == 'owner' and value.endswith('>'):
            value = value.replace('<@', '')
            value = value.replace('>', '')

        # let's play the search game

        char_list = db.get_characters_by_search(field=field, value=value)

        # gets the search data and sets up the buttons.
        value = value.replace('-', ' ')
        search_str, components = await self.build_string(inter, char_list, 1, field, value)

        embed = disnake.Embed(title=f"Search Results",
                              description=f"{len(char_list)} Characters Matched the Query.{search_str}")
        await inter.send(embed=embed, components=components)

    # List Command
    # I'm doing both commands in one function because they're very similar functionally.
    @commands.slash_command(name='list')
    async def list_characters(self, inter: disnake.ApplicationCommandInteraction, owner: disnake.Member = None):
        if owner:
            char_list = db.get_characters_by_owner(owner)
            search_str, components = await self.build_string(inter, char_list, 1, 'owner', owner.id)
        else:
            char_list = db.get_all_characters()
            search_str, components = await self.build_string(inter, char_list, 1, 'allcharacters', 'invalid')
        embed = disnake.Embed(title=f"Search Results",
                              description=f"{len(char_list)} Characters Matched the Query.{search_str}")
        await inter.send(embed=embed, components=components)

    @commands.Cog.listener("on_button_click")
    async def search_button_handler(self, inter: disnake.MessageInteraction):
        if not inter.data.custom_id.startswith('search-'):
            return

        split_data = inter.data.custom_id.split('-')

        if int(split_data[1]) != inter.author.id:
            await inter.send("Only the person who called /search can do this!", ephemeral=True)
            return

        page = int(split_data[2])
        action = split_data[3]
        field = split_data[4]
        value = split_data[5]

        if action == 'select':
            modal_components = [disnake.ui.TextInput(label='Enter Page Number', custom_id=f"page")]
            await inter.response.send_modal(title='Enter Page Number',
                                            custom_id=f'smodal-{inter.author.id}-{field}-{value}',
                                            components=modal_components)
            return

        if action == 'superleft':
            page -= 5
        elif action == 'left':
            page -= 1
        elif action == 'right':
            page += 1
        elif action == 'superright':
            page += 5

        if field == 'allcharacters':
            char_list = db.get_all_characters()
        else:
            char_list = db.get_characters_by_search(field=field, value=value)

        if page < 1:
            page = 1
        if page > int(len(char_list) / 25) + 1:
            page = int(len(char_list) / 25) + 1

        search_str, components = await self.build_string(inter, char_list, page, field, value)
        embed = disnake.Embed(title=f"Search Results",
                              description=f"{len(char_list)} Characters Matched the Query.{search_str}")
        await inter.response.edit_message(embed=embed, components=components)

    @commands.Cog.listener("on_modal_submit")
    async def on_search_modal_submit(self, inter: disnake.ModalInteraction):
        if not inter.data.custom_id.startswith('smodal-'):
            return

        split_data = inter.data.custom_id.split('-')

        if int(split_data[1]) != inter.author.id:
            await inter.send("Only the person who called /search can do this!", ephemeral=True)
            return

        page = inter.text_values[list(inter.text_values.keys())[0]]
        page = int(page)
        field = split_data[2]
        value = split_data[3]

        if field == 'allcharacters':
            char_list = db.get_all_characters()
        else:
            char_list = db.get_characters_by_search(field=field, value=value)

        if page < 1:
            page = 1
        if page > int(len(char_list) / 25) + 1:
            page = int(len(char_list) / 25) + 1

        search_str, components = await self.build_string(inter, char_list, page, field, value)
        embed = disnake.Embed(title=f"Search Results",
                              description=f"{len(char_list)} Characters Matched the Query.{search_str}")
        await inter.response.edit_message(embed=embed, components=components)


def setup(bot):
    bot.add_cog(Search(bot))
