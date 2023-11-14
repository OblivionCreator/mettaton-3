import json
import io
import disnake
import validators


class Character:
    # Character Fields
    _character_id: str | None
    _owner: int | None
    _status: str | None
    name: str | None
    age: str | None
    gender: str | None
    abilities: str | None
    appearance: str | None
    species: str | None
    background: str | None
    personality: str | None
    prefilled: str | None
    misc: dict | None

    def __init__(self, char_id=None, owner=None, status=None, name=None, age=None, gender=None, abilities=None,
                 appearance=None,
                 species=None, background=None, personality=None, prefilled=None, misc=None):
        self._character_id = char_id
        self._owner = owner
        self._status = status
        self.name = name
        self.age = age
        self.gender = gender
        self.species = species
        self.abilities = abilities
        self.appearance = appearance
        self.background = background
        self.personality = personality
        self.prefilled = prefilled
        temp_misc = self.create_custom_fields(misc)
        self.misc = {}
        for key, value in temp_misc.items():
            self.misc[key] = value
        for key, value in vars(self).items():
            if value is None and key != 'misc' and key != 'prefilled':
                setattr(self, key, 'Not set!')

    def create_custom_fields(self, misc):
        if not misc:
            return {}
        else:
            try:
                return json.loads(misc)
            except Exception as e:
                return {}

    def get_character_view(self, guild:disnake.Guild):

        embed = disnake.Embed(title=f"Viewing Character ID {self._character_id}.")
        # Returns a disnake.Embed object based on the current fields.
        for key, value in vars(self).items():
            if key == 'misc':
                continue  # Does not show the 'misc' variable, as this is just JSON.
            value = str(value)

            if value is None or value == '' or value == 'None':
                continue  # Skips if the value is None.

            # Adds a space to _character_id, and removes leading underscore

            if key.lower() == '_character_id':  # this is gross.
                key = 'Character ID'

            key = key.lstrip('_')
            key = key.replace('_', ' ')

            if key.lower() == 'owner':
                member = guild.get_member(int(value))
                if member:
                    value = member.name.title()
                else:
                    value += ' (User has left the server.)'

            if len(value) > 1021:
                value = value[0:1020] + '...'

            embed.add_field(name=key.title(), value=value[0:1024], inline=False)
        for key, value in self.misc.items():
            # Checks for specific fields. - Portrait is the image.
            if key.lower() == 'portrait':
                embed.set_image(value)
                continue

            embed.add_field(name=key, value=value[0:1024], inline=False)

        if self._status == 'New':
            embed.set_footer(text=f"The given Character ID {self._character_id} is not final and will change once the character is submitted.")

        if self._status == 'New' or self._status == 'Registering':
            embed.description = "You must complete all the default fields before you can submit your character. You can hit the + and - buttons to add or remove custom fields."

        return embed

    def get_field_view(self, character_id: int, field: str):
        image = None
        if field in vars(self).keys():
            field_data = getattr(self, field.lower())
            field = field.title()
            field.lstrip('_')
        else:
            # Check if it's in self.misc instead.
            field_data = self.misc[field]
            if validators.url(field_data):
                image = field_data  # thanks to discord doing all the url verification for me, i can just feed this in there and discord will handle it instead. Score!
                # nvm no it doesn't - 11/11/23

        embed = disnake.Embed(title=f"Viewing field {field} for ID {character_id}", description=field_data)
        embed.set_image(image)
        return embed
