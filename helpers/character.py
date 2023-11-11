import json
import io
import disnake


class Character:
    # Character Fields
    character_id: str | None
    owner: int | None
    status: str | None
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
        self.character_id = char_id
        self.owner = owner
        self.status = status
        self.name = name
        self.age = age
        self.gender = gender
        self.abilities = abilities
        self.appearance = appearance
        self.species = species
        self.background = background
        self.personality = personality
        self.prefilled = prefilled
        temp_misc = self.create_custom_fields(misc)
        self.misc = {}
        for key, value in temp_misc.items():
            self.misc[key.lower()] = value


    def create_custom_fields(self, misc):
        if not misc:
            return {}
        else:
            try:
                return json.loads(misc)
            except Exception as e:
                return {}

    def get_character_view(self):

        embed = disnake.Embed(title=f"Viewing Character ID {self.character_id}.")
        # Returns a disnake.Embed object based on the current fields.
        output_to_file = False
        character_string = ''
        for key, value in vars(self).items():
            if key == 'misc' or key == 'friendly_names':
                continue  # Does not show the 'misc' variable, as this is just JSON.
            value = str(value)

            if value is None or value == '' or value == 'None':
                continue  # Skips if the value is None.

            if len(value) > 1024:
                output_to_file = True  # Outputs character to a file.

            embed.add_field(name=key.title(), value=value[0:1024], inline=False)
            character_string += f'{character_string}\n{key}: {value}'
        for key, value in self.misc.items():
            # Checks for specific fields. - Portrait is the image.
            if key.lower() == 'portrait':
                embed.set_image(value)
                continue

            if len(value) > 1024:
                output_to_file = True
            embed.add_field(name=key, value=value[0:1024], inline=False)

        # Writes all fields to a file if any are too long.
        if output_to_file:
            embed.add_field(name="This character was too long to display!", value="Please see the attached txt file to view full character.", inline=False)
            bb = io.BytesIO(character_string.encode("utf-8"))
            file = disnake.File(bb)
        else:
            file = None
        return embed, file

    def get_field_view(self,character_id:int, field:str):
        image = None
        if field in vars(self).keys():
            field_data = getattr(self, field.lower())
        else:
            # Check if it's in self.misc instead.
            field_data = self.misc[field.lower()]
            image = field_data # thanks to discord doing all the url verification for me, i can just feed this in there and discord will handle it instead. Score!

        embed = disnake.Embed(title=f"Viewing field {field.title()} for ID {character_id}", description=field_data)
        embed.set_image(image)
        return embed