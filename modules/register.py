import disnake
from disnake.ext import commands
import random
class Template(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

commands.slash_command(name="newregister", guild_ids=[770428394918641694, 363821745590763520])
async def newregister(inter, character_id: int = None):
    identifier = f"{inter.author.id}.{random.randint(1, 10000)}"
    application_embed = disnake.Embed(color=disnake.Color.yellow())
    field_data = {"Owner": f"{inter.author}", "Status": "Pending", "Name": "", "Age": "", "Gender": "",
                  "Abilities/Tools": "", "Appearance": "", "Species": "", "Backstory": "", "Personality": ""}
    custom_fields = {}
    canon_chars = getDenyList()
    if character_id:
        temp_data = _getCharDict(character_id)
        if isinstance(temp_data, dict) and temp_data[getLang("Fields", "owner")] == inter.author.id:
            for field in temp_data:
                if not temp_data[field]:
                    continue
                else:
                    application_embed.add_field(name=field, value=temp_data[field])
        else:
            character_id = 0
    else:
        character_id = 0
        for fi in field_data:
            application_embed.add_field(name=f"{fi}", value=f"{field_data[fi]}", inline=False)
        application_embed.title = f"Preview for ID {character_id}"

    register_ar_1 = disnake.ui.ActionRow(
        disnake.ui.Button(label="Basic Info", style=disnake.ButtonStyle.blurple,
                          custom_id=f"basic-info_{identifier}"),
        disnake.ui.Button(label="Details", style=disnake.ButtonStyle.blurple,
                          custom_id=f"details_{identifier}"),
        disnake.ui.Button(label="Add Field", style=disnake.ButtonStyle.grey,
                          custom_id=f"add-field_{identifier}")
    )
    register_ar_2 = disnake.ui.ActionRow(
        disnake.ui.Button(label="Submit", style=disnake.ButtonStyle.green, custom_id=f"submit_{identifier}",
                          disabled=True),
        disnake.ui.Button(label="Cancel", style=disnake.ButtonStyle.red, custom_id=f"cancel_{identifier}")
    )
    i_channel = inter.channel
    app_thread = await i_channel.create_thread(name="Character Registration",
                                               type=disnake.ChannelType.private_thread)
    app_message = await app_thread.send(f"Hi, {inter.author.mention}! Welcome to character registration.",
                                        embed=application_embed, components=[register_ar_1, register_ar_2],
                                        allowed_mentions=disnake.AllowedMentions(users=True))
    await inter.response.send_message(f"Started character creation in {app_thread.mention}!", ephemeral=True)

    async def update_preview(embed_inter, info):
        embed = embed_inter.embeds[0].copy()
        embed_len = await get_embed_len(embed)
        for f in range(len(embed.fields)):
            if embed.fields[f].name in info.keys():
                key = embed.fields[f].name
                if len(info[key]) > 1024:
                    embed.set_field_at(f, name=key, value="[TOO LARGE FOR PREVIEW]", inline=False)
                elif embed_len + len(info[key]) > 6000:
                    await trailing_preview(embed_inter)
                else:
                    embed.set_field_at(f, name=key, value=info[key], inline=False)
        await embed_inter.edit(embed=embed)

    async def trailing_preview(embed_inter):
        embed = embed_inter.embeds[0].copy()
        reduction_size = 512
        long_fields = []
        for f in range(len(embed.fields)):
            if len(embed.fields[f].value) > 512:
                long_fields.append(f)
        for f in long_fields:
            embed.set_field_at(f, name=embed.fields[f].name,
                               value=f"{embed.fields[f].value[0:reduction_size - 1]}...", inline=False)
        await embed_inter.edit(embed=embed)

    async def get_embed_len(embed):
        embed_len = 0
        for f in embed.fields:
            embed_len += len(f.value)
        return embed_len

    async def check_completion(inter_msg, ar, fields_dict):
        completed = True
        for f in fields_dict:
            if fields_dict[f] == "":
                completed = False
        if completed:
            submit_button, cancel_button = ar.children
            submit_button.disabled = False
            ar.clear_items()
            ar.append_item(submit_button)
            ar.append_item(cancel_button)
            await inter_msg.edit(components=[register_ar_1, ar])

    async def check_cfield_no(inter_msg, ar, cfields_dict):
        buttons = []
        cbutton_hidden = True
        for c in ar.children:
            buttons.append(c)
        for b in range(len(buttons)):
            if buttons[b].custom_id == f"custom_{identifier}":
                cbutton_i = b
                cbutton_hidden = False
            if buttons[b].custom_id == f"remove-field_{identifier}":
                rbutton_i = b
        if (len(cfields_dict) == 0) and (buttons[cbutton_i].disabled is not True):
            del buttons[cbutton_i]
            del buttons[rbutton_i - 1]
            ar.clear_items()
            for but in buttons:
                ar.append_item(but)
            await inter_msg.edit(components=[ar, register_ar_2])
        elif (len(cfields_dict) > 0) and (cbutton_hidden is True):
            buttons.insert(2, disnake.ui.Button(label="Custom", style=disnake.ButtonStyle.blurple,
                                                custom_id=f"custom_{identifier}"))
            buttons.insert(4, disnake.ui.Button(label="Remove Field", style=disnake.ButtonStyle.grey,
                                                custom_id=f"remove-field_{identifier}"))
            ar.clear_items()
            for but in buttons:
                ar.append_item(but)
            await inter_msg.edit(components=[ar, register_ar_2])

    class RegisterBasicInfoFields(disnake.ui.Modal):
        def __init__(self):
            components = [
                disnake.ui.TextInput(
                    label="Character Name",
                    placeholder="The name of your character.",
                    custom_id="Name",
                    style=disnake.TextInputStyle.short,
                    max_length=50,
                    value=f"{field_data['Name']}"
                ),
                disnake.ui.TextInput(
                    label="Character Age",
                    placeholder="The age of your character.",
                    custom_id="Age",
                    style=disnake.TextInputStyle.short,
                    max_length=50,
                    value=f"{field_data['Age']}"
                ),
                disnake.ui.TextInput(
                    label="Character Gender",
                    placeholder="Your character's gender.",
                    custom_id="Gender",
                    style=disnake.TextInputStyle.short,
                    max_length=50,
                    value=f"{field_data['Gender']}"
                ),
                disnake.ui.TextInput(
                    label="Character Species",
                    placeholder="Your character's species.",
                    custom_id="Species",
                    style=disnake.TextInputStyle.short,
                    max_length=50,
                    value=f"{field_data['Species']}"
                ),
            ]
            super().__init__(title="Basic Info", components=components)

        # The callback received when the user input is completed.
        async def callback(self, inter: disnake.ModalInteraction):
            not_allowed = False
            for key, value in inter.text_values.items():
                if value in canon_chars:
                    await inter.response.send_message("Canon characters are not allowed!", ephemeral=True)
                    not_allowed = True
            if not not_allowed:
                for key, value in inter.text_values.items():
                    if key in field_data.keys():
                        field_data[key] = value
                await check_completion(app_message, register_ar_2, field_data)
                await update_preview(app_message, field_data)
                await inter.response.send_message(f"Character's basic info has been edited!", ephemeral=True)

    class RegisterDetailsFields(disnake.ui.Modal):
        def __init__(self):
            components = [
                disnake.ui.TextInput(
                    label="Character Abilities and Tools",
                    placeholder="Describe the strengths and weaknesses of your character's abilities and tools.",
                    custom_id="Abilities/Tools",
                    style=disnake.TextInputStyle.paragraph,
                    value=f"{field_data['Abilities/Tools']}"
                ),
                disnake.ui.TextInput(
                    label="Character Appearance",
                    placeholder="Your character's appearance.",
                    custom_id="Appearance",
                    style=disnake.TextInputStyle.paragraph,
                    value=f"{field_data['Appearance']}"
                ),
                disnake.ui.TextInput(
                    label="Character Backstory",
                    placeholder="The events leading up to your character's introduction into the RP.",
                    custom_id="Backstory",
                    style=disnake.TextInputStyle.paragraph,
                    value=f"{field_data['Backstory']}"
                ),
                disnake.ui.TextInput(
                    label="Character Personality",
                    placeholder="Your character's personality.",
                    custom_id="Personality",
                    style=disnake.TextInputStyle.paragraph,
                    value=f"{field_data['Personality']}"
                ),
            ]
            super().__init__(title="Details", components=components)

        async def callback(self, inter: disnake.ModalInteraction):
            for key, value in inter.text_values.items():
                if key in field_data.keys():
                    field_data[key] = value
            await check_completion(app_message, register_ar_2, field_data)
            await update_preview(app_message, field_data)
            await inter.response.send_message(f"Character's details have been edited!", ephemeral=True)

    class RegisterCustomFields(disnake.ui.Modal):
        def __init__(self):
            components = []
            for c in custom_fields:
                ti = disnake.ui.TextInput(
                    label=c,
                    custom_id=c,
                    style=disnake.TextInputStyle.paragraph,
                    value=custom_fields[c]
                )
                components.append(ti)
            super().__init__(title="Custom Fields", components=components)

        async def callback(self, inter: disnake.ModalInteraction):
            for key, value in inter.text_values.items():
                custom_fields[key] = value
            await update_preview(app_message, custom_fields)
            await inter.response.send_message(f"Character's custom fields have been edited!", ephemeral=True)

    class RegisterNewField(disnake.ui.Modal):
        def __init__(self):
            components = [
                disnake.ui.TextInput(
                    label="New Field Name",
                    placeholder="The title of your custom field.",
                    custom_id="New Field Name",
                    style=disnake.TextInputStyle.short,
                ),
                disnake.ui.TextInput(
                    label="New Field Text",
                    placeholder="The contents of your custom field.",
                    custom_id="New Field Text",
                    style=disnake.TextInputStyle.paragraph,
                )
            ]
            super().__init__(title="New Custom Field", components=components)

        async def callback(self, inter: disnake.ModalInteraction):
            app_embed = app_message.embeds[0].copy()
            new_field = []
            dupe_field = False
            for key, value in inter.text_values.items():
                new_field.append(value)
            for f in app_embed.fields:
                if f.name == new_field[0]:
                    await inter.response.send_message("A field already exists with that name!", ephemeral=True)
                    dupe_field = True
            if not dupe_field:
                custom_fields[new_field[0]] = new_field[1]
                embed_len = await get_embed_len(app_embed)
                if embed_len + len(new_field[1]) > 6000:
                    await trailing_preview(embed_inter)
                app_embed.add_field(name=new_field[0], value=new_field[1])
                await check_cfield_no(app_message, register_ar_1, custom_fields)
                await update_preview(app_message, custom_fields)
                await inter.response.send_message(f"Custom field has been added to application!", ephemeral=True)

    class RegisterRemoveMenu(disnake.ui.Select):
        def __init__(self):
            options = []
            for c in custom_fields:
                option = disnake.SelectOption(
                    label=c,
                    value=f"cfield_{identifier}_{c}"
                )
                options.append(option)
            super().__init__(options=options, placeholder="Field to delete...")

    @commands.Cog.listener("on_dropdown")
    async def on_misc_remove(inter):
        app_embed = app_message.embeds[0].copy()
        if inter.data.values[0].startswith(f"cfield_{identifier}"):
            cfield = inter.data.values[0].split("_")[-1]
            del custom_fields[cfield]
            for f in range(len(app_embed.fields)):
                if app_embed.fields[f].name == cfield:
                    app_embed.remove_field(f)
                    await app_message.edit(embed=app_embed)
            await check_cfield_no(app_message, register_ar_1, custom_fields)
            await inter.response.send_message(f"Custom field has been removed from application!", ephemeral=True)

    @commands.Cog.listener("on_button_click")
    async def on_register_button_click(inter):
        if inter.data.custom_id == f"basic-info_{identifier}":
            await inter.response.send_modal(modal=RegisterBasicInfoFields())
        elif inter.data.custom_id == f"details_{identifier}":
            await inter.response.send_modal(modal=RegisterDetailsFields())
        elif inter.data.custom_id == f"custom_{identifier}":
            await inter.response.send_modal(modal=RegisterCustomFields())
        elif inter.data.custom_id == f"add-field_{identifier}":
            if len(custom_fields) > 5:
                await inter.response.send_message("You've already made the maximum number of custom fields!")
            else:
                await inter.response.send_modal(modal=RegisterNewField())
        elif inter.data.custom_id == f"remove-field_{identifier}":
            await inter.response.send_message("What custom field would you like to delete?",
                                              components=RegisterRemoveMenu())
        elif inter.data.custom_id == f"cancel_{identifier}":
            await inter.response.send_message("Are you sure you want to cancel character creation?", components=[
                disnake.ui.Button(label="Yes", style=disnake.ButtonStyle.green,
                                  custom_id=f"confirm_cancel_{identifier}"),
                disnake.ui.Button(label="No", style=disnake.ButtonStyle.red, custom_id=f"abort_cancel_{identifier}")
            ])
        elif inter.data.custom_id == f"confirm_cancel_{identifier}":
            await inter.response.send_message("Character creation has been stopped.")
        elif inter.data.custom_id == f"abort_cancel_{identifier}":
            await inter.response.send_message("Cancellation aborted.", delete_after=5)
            # cancel_message = await inter.original_response()
            # await disnake.Message.delete(cancel_message, delay=5)
        elif inter.data.custom_id == f"submit_{identifier}":
            await inter.response.send_message("Placeholder 'character has been submitted' message.")

def setup(bot):
    bot.add_cog(Template(bot))
