import json


class Character:

    # Character Fields
    char_id: str
    owner: int
    status: str
    name: str | None
    age: str | None
    gender: str | None
    abilities: str | None
    appearance: str | None
    species: str | None
    background: str | None
    personality: str | None
    prefilled: str | None
    misc: str | None

    def __init__(self, char_id, owner, status, name=None, age=None, gender=None, abilities=None, appearance=None,
                 species=None, background=None, personality=None, prefilled=None, misc=None):
        self.char_id = char_id
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
        self.misc = misc
        self.create_custom_fields(misc)

    def create_custom_fields(self, misc):
        if not misc:
            return
        custom_field_dict = json.loads(misc)
        for key, value in custom_field_dict.items():
            setattr(self, key, value)