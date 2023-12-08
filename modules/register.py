import typing

import disnake
from disnake.ext import commands
from helpers import character, database, config, getdiff

db = database.Database()
conf = config.Config()


class Register(commands.Cog):
    characters: dict

    def __init__(self, bot):
        self.bot = bot

    def set_components(self, inter: disnake.ApplicationCommandInteraction, char: character.Character):
        options = []
        for o in vars(char).keys():
            # Does not add immutable fields to the list as they're always kinda the same.
            # Does not add 'misc' to the list as this is just JSON.
            if o == 'misc' or o.startswith('_'):
                continue

            # Does not add 'prefilled' to the list, unless it is already set.
            if o == 'prefilled' and (getattr(char, o) is None or getattr(char, o) == ''):
                continue

            o.replace("_", " ")
            options.append(o.title())
        for o in char.misc.keys():
            options.append(o)

        components = []
        # Dropdown to select the fields
        components.append(disnake.ui.StringSelect(placeholder="Select a field to edit", options=options,
                                                  custom_id=f'register-select-{char._character_id}-{inter.author.id}'))

        row1 = disnake.ui.ActionRow()
        row2 = disnake.ui.ActionRow()

        # Adds 4 buttons
        # New Field - Creates a new misc field

        if len(char.misc) >= 10:
            disable_button = True
        else:
            disable_button = False
        row1.add_button(label='+', style=disnake.ButtonStyle.green,
                        custom_id=f'rbutton-newfield-{char._character_id}-{inter.author.id}', disabled=disable_button)

        # Remove Field - Removes a misc field

        if len(char.misc) == 0:
            disable_button = True
        else:
            disable_button = False
        row1.add_button(label='-', style=disnake.ButtonStyle.red,
                        custom_id=f'rbutton-removefield-{char._character_id}-{inter.author.id}',
                        disabled=disable_button)

        # Submit - Finishes the registration

        disable_button = False

        for value in vars(char):
            if value.startswith('_') or value == 'misc' or value == 'prefilled':
                continue
            if vars(char)[value] == 'Not set!':
                disable_button = True
                break

        row2.add_button(label='✅Submit', style=disnake.ButtonStyle.blurple,
                        custom_id=f'rbutton-submit-{char._character_id}-{inter.author.id}', disabled=disable_button)
        # Cancel - Cancels the registration and deletes the character.
        row2.add_button(label='Discard', style=disnake.ButtonStyle.red,
                        custom_id=f'rbutton-cancel-{char._character_id}-{inter.author.id}')

        components.append(row1)
        components.append(row2)

        return components

    @commands.slash_command()
    async def reregister(self, inter: disnake.ApplicationCommandInteraction, character_id:int):
        await self.register(inter, character_id)

    @commands.slash_command()
    async def register(self, inter: disnake.ApplicationCommandInteraction, character_id: int | None = None):
        new_character, thread, = db.register_character(author_id=inter.author.id, character_id=character_id)
        thread, = thread
        embed = new_character.get_character_view(guild=inter.guild)

        # Returns if the character is owned by someone else.
        if int(new_character._owner) != inter.author.id:
            await inter.send(f"You cannot register a character owned by another person!", ephemeral=True)
            return

        # Gets the register channel.
        register_channel = self.bot.get_channel(conf.register_channel)

        # Creates a private thread for this character registration.
        if not thread:
            thread = await register_channel.create_thread(
                name=f"{inter.author.name.title()}'s Character Registration",
                type=disnake.ChannelType.private_thread)
            db.update_register_character(new_character, thread)
        else:
            thread = register_channel.get_thread(thread)

        # Logs the registration & thread in logging channel
        log_channel = inter.guild.get_channel(conf.log_channel)
        if log_channel:
            await log_channel.send(f"{inter.author.name.title()} started character registration in {thread.mention}")

        # Gets the components for the registration view.
        components = self.set_components(inter=inter, char=new_character)

        # Sends the registration view to the thread.
        await thread.send(inter.author.mention, embed=embed, components=components)
        await inter.send(f"Character registration has been started in {thread.mention}", ephemeral=True)

    @commands.Cog.listener("on_dropdown")
    async def dropdown_listener(self, inter: disnake.MessageInteraction):
        if not inter.data.custom_id.startswith('register'):
            return

        split_data = inter.data.custom_id.split('-')

        character_id = int(split_data[2])
        character = db.get_registering_character_by_id(character_id)

        if not character:
            await inter.send("The character wasn't found! Has it been deleted..?", ephemeral=True)
            return

        if inter.author.id != int(split_data[3]):
            # this shouldn't be theoretically possible but just in case
            # someone gives someone else access to their registration thread somehow
            await inter.send("Only the person who called /register can do this!", ephemeral=True)
            return

        if split_data[1] == 'select':
            if inter.data.values[0].lower() in vars(character).keys():
                value = getattr(character, inter.data.values[0].lower())
            else:
                # This means it's a custom field
                value = character.misc[inter.data.values[0]]

            modal_components = disnake.ui.TextInput(label=inter.data.values[0], value=value, required=True,
                                                    style=disnake.TextInputStyle.long,
                                                    custom_id=inter.data.values[0])
            await inter.response.send_modal(title=f'Registration for Character ID {character_id}',
                                            custom_id=f'rmodal-modify-{character_id}-{inter.author.id}',
                                            components=modal_components)
        elif split_data[1] == 'remove':
            character.misc.pop(inter.data.values[0])
            db.update_register_character(character, thread=inter.channel)
            # Edits the original message sent to user.
            message = await inter.channel.fetch_message(int(split_data[4]))
            await message.edit(embed=character.get_character_view(guild=inter.guild),
                               components=self.set_components(inter=inter, char=character))
            await inter.response.edit_message(content=f"Field {inter.data.values[0]} has been removed!", components=[])

    @commands.Cog.listener("on_modal_submit")
    async def register_modal(self, inter: disnake.ModalInteraction):
        if not inter.data.custom_id.startswith('rmodal'):
            return

        split_data = inter.data.custom_id.split('-')
        temp, modal_type, character_id, author_id = split_data
        character = db.get_registering_character_by_id(int(character_id))
        if not character:
            await inter.send("The character wasn't found! Has it been deleted..?", ephemeral=True)
            return
        if inter.author.id != int(author_id):
            await inter.send("Only the person who called /register can do this!", ephemeral=True)
            return

        if modal_type == 'modify':
            if list(inter.text_values.keys())[0].lower() in vars(character).keys():
                setattr(character, list(inter.text_values)[0].lower(), inter.text_values[list(inter.text_values)[0]])
            else:
                character.misc[list(inter.text_values)[0]] = inter.text_values[list(inter.text_values)[0]]

            db.update_register_character(character, thread=inter.channel)
            embed = character.get_character_view(guild=inter.guild)
            await inter.response.edit_message(embed=embed, components=self.set_components(inter=inter, char=character))
            return
        elif modal_type == 'add':
            if inter.text_values['value'].lower() in vars(character).keys():
                await inter.send("This field already exists! Please select it from the dropdown list.", ephemeral=True)
                return
            character.misc[inter.text_values['value']] = inter.text_values['description']
            db.update_register_character(character, thread=inter.channel)
            embed = character.get_character_view(guild=inter.guild)
            await inter.response.edit_message(embed=embed, components=self.set_components(inter=inter, char=character))
        elif modal_type == 'remove':
            pass

    @commands.Cog.listener("on_button_click")
    async def button_listener(self, inter: disnake.MessageInteraction):
        if not inter.data.custom_id.startswith('rbutton'):
            return

        split_data = inter.data.custom_id.split('-')

        if int(split_data[3]) != inter.author.id and split_data[1] != 'vote':
            await inter.send("Only the person who called /register can do this!", ephemeral=True)
            return

        # Now let's play "determine what happen"

        char = db.get_registering_character_by_id(int(split_data[2]))

        if split_data[1] == 'newfield':
            # Sends user a modal to create a new field. Modal contains field name (short) and field description (long)
            modal_components = []
            modal_components.append(
                disnake.ui.TextInput(label='New Field Title', required=True, style=disnake.TextInputStyle.short,
                                     custom_id=f'value', max_length=100))
            modal_components.append(
                disnake.ui.TextInput(label='New Field Description', required=True, style=disnake.TextInputStyle.long,
                                     custom_id=f'description'))
            await inter.response.send_modal(title='Creating new Field.',
                                            custom_id=f'rmodal-add-{split_data[2]}-{inter.author.id}',
                                            components=modal_components)
            return
        elif split_data[1] == 'removefield':
            # Sends user a modal with a dropdown of all the current custom fields.
            modal_components = []
            options = []

            for o in char.misc.keys():
                options.append(o)
            # Dropdown to select the fields

            modal_components.append(disnake.ui.StringSelect(placeholder="Select a field to remove", options=options,
                                                            custom_id=f'register-remove-{split_data[2]}-{inter.author.id}-{inter.message.id}'))
            await inter.response.send_message(
                'Choose the field you wish to remove.\nAll contents of this field will be lost!', ephemeral=True,
                components=modal_components)
            return
        elif split_data[1] == 'submit':
            char._status = 'Pending'
            old_char = db.get_character_by_id(char._character_id)
            db.update_register_character(char, thread=inter.channel)
            final_id = db.finish_character(char)

            # let's delete the votes just in case it was already in pending.
            db.clear_votes(char._character_id)

            char._character_id = final_id
            gm_role = inter.guild.get_role(conf.gamemaster_role)
            gm_channel = inter.guild.get_channel(conf.alert_channel)
            await inter.message.edit(embed=char.get_character_view(guild=inter.guild), components=[])
            flags = disnake.MessageFlags()
            flags.suppress_notifications = True

            # Adds in a diffchecker URL if it is a reregister
            diffcheck = ''
            if old_char:
                if old_char._character_id == final_id:
                    old_char_str = ''
                    old_char_dict = vars(old_char)
                    for key in old_char_dict.keys():
                        old_char_str += f'{key}: {old_char_dict[key]}\n'
                    for key in old_char.misc:
                        old_char_str += f'{key}: {old_char.misc[key]}\n'

                    new_char_str = ''
                    new_char_dict = vars(char)
                    for key in new_char_dict.keys():
                        new_char_str += f'{key}: {new_char_dict[key]}\n'
                    for key in char.misc:
                        new_char_str += f'{key}: {char.misc[key]}\n'

                    diffcheck = '\n' + getdiff.get_difference_url(left=old_char_str, right=new_char_str, title=f'Differences in Character {char._character_id}')

            # Adds voting buttons

            components = [
                disnake.ui.Button(label='+1', custom_id=f'rbutton-vote-{char._character_id}-{inter.author.id}-up'),
                disnake.ui.Button(label='-1', custom_id=f'rbutton-vote-{char._character_id}-{inter.author.id}-down')]
            await inter.send(
                content=f"Your character has been submitted with ID {final_id} and is currently pending review by the GMs.\nThis thread will now be used for discussion regarding your character with the {gm_role.mention}s.",
                components=[], flags=flags, allowed_mentions=disnake.AllowedMentions(roles=True))
            message = await gm_channel.send(
                f"Character Submitted with ID {final_id}\nAny fields that were too long to be displayed have been sent in the attached thread.{diffcheck}",
                embed=char.get_character_view(guild=inter.guild), components=components)
            thread = await message.create_thread(name=f'Detailed Information for Character ID {final_id}')

            await inter.channel.edit(name=f"#{char._character_id} - {char.name}")

            for field in vars(char).keys():
                if field == 'misc':
                    continue
                if vars(char)[field] is None or vars(char)[field] == '' or vars(char)[field] == 'None' or len(
                        str(vars(char)[field])) <= 1024:
                    continue  # Does not add if it's an empty field, or if it's not overflowed.

                embed = char.get_field_view(character_id=char._character_id, field=field)
                await thread.send(embed=embed)
            for key in char.misc.keys():
                if len(char.misc[key]) <= 1024:
                    continue
                embed = char.get_field_view(character_id=char._character_id, field=key)
                await thread.send(embed=embed)
            return
        elif split_data[1] == 'cancel':
            # db.delete_registering_character(char._character_id)
            await inter.send("Character registration has been cancelled.", ephemeral=True)
            await inter.message.edit(components=[])
            return
        elif split_data[1] == 'vote':
            if split_data[4] == 'up':
                db.add_vote(character_id=int(split_data[2]), author=inter.author.id, positive=inter.author.id)
            elif split_data[4] == 'down':
                db.add_vote(character_id=int(split_data[2]), author=inter.author.id, negative=inter.author.id)

            votes = db.get_votes(split_data[2])
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
            check = ''
            if character_score >= conf.vote_threshold:
                check = '\nThis character has enough votes to be approved! Do `/approve` to approve this character.'
            elif character_score <= - conf.vote_threshold:
                check = '\nThis character has enough votes to be denied! Do `/deny` to deny this character.'
            await inter.send(
                f"Character {split_data[2]} now has a voting total of {character_score}{check} ({positive_votes_score} For, {negative_votes_score} Against)\nTo view more detailed information, do `/votes`",
                ephemeral=True)


def setup(bot):
    bot.add_cog(Register(bot))
