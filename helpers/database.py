import json
import sqlite3
import os
from helpers import character

import disnake

db_filename = "./mttchars.db"


def make_database(file: str):
    schema = open("./schema.sql", "r").read()
    db = sqlite3.connect(file)
    db.executescript(schema)
    db.commit()


class Database:
    db: sqlite3.Connection

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Database, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        if not os.path.exists(db_filename):
            make_database(db_filename)
        self.db = sqlite3.connect(db_filename)

    # Gets a single character by ID if status is not Disabled.
    def get_character_by_id(self, character_id: int):
        cur = self.db.execute("SELECT * FROM charlist WHERE charID = ?", (character_id,))
        # Converts the character into a character.Character object.
        local_ch = cur.fetchone()
        if local_ch:
            return character.Character(*local_ch)
        else:
            return None
    # Returns all characters that contain the specified value in the specified field.
    def get_characters_by_search(self, field: str, value: str):
        # Searches all fields and returns all characters that contain the specified value
        cur = self.db.execute("SELECT charID, owner, name, status FROM charlist WHERE ? LIKE ?", (field, f"%{value}%"))
        return cur.fetchall()

    # Returns all characters that belong to the specified owner.
    def get_characters_by_owner(self, owner: disnake.Member):
        cur = self.db.execute("SELECT charID, owner, name, status FROM charlist WHERE ownerID = ?", (owner.id,))
        return cur.fetchall()

    # Creates a new character from a character.Character object and returns the ID.
    def create_character(self, char: character.Character):

        cur = self.db.execute("INSERT INTO charlist (owner, status, name, age, gender, abilities, appearance, "
                       "species, backstory, personality, prefilled, misc) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", [char.owner, char.status, char.name, char.age, char.gender, char.abilities, char.appearance, char.species, char.background, char.personality, char.prefilled, char.misc])
        self.db.commit()
        return cur.lastrowid

    # Updates fields of an existing character and returns the ID.
    def update_character(self, char: character.Character):
        js_misc = json.dumps(char.misc)
        cur = self.db.execute("UPDATE charlist SET owner = ?, status = ?, name = ?, age = ?, gender = ?, "
                       "abilities = ?, appearance = ?, species = ?, backstory = ?, personality = ?, prefilled = ?, misc = ? "
                       "WHERE charID = ?", [char.owner, char.status, char.name, char.age, char.gender, char.abilities, char.appearance, char.species, char.background, char.personality, char.prefilled, js_misc, char.character_id])
        self.db.commit()
        return cur.lastrowid

    def get_or_create_character(self, author_id:int, character_id:int | None = None):
        # Gets a character if it exists, else creates a new character with that ID.
        cur = self.db.execute("SELECT * FROM charlist WHERE charID = ?", [character_id])
        char_temp = cur.fetchone()
        if char_temp:
            return character.Character(*char_temp)
        else:
            if not character_id:
                cur = self.db.execute("INSERT INTO charlist (owner, status) VALUES (?, ?)", [author_id, "Registering"])
            else:
                cur = self.db.execute("INSERT INTO charlist (charID, owner, status) VALUES (?, ?, ?)", [character_id, author_id, "Registering"])
            self.db.commit()
            character_id = cur.lastrowid
            return self.get_character_by_id(character_id)

    def disable_character(self, character_id: int):
        # Moves character info to the deleted-chars table.
        cur = self.db.execute("INSERT INTO deleted_chars SELECT * FROM charlist WHERE charID = ?", (character_id,))
        cur = self.db.execute("DELETE FROM charlist WHERE charID = ?", (character_id,))
        self.db.commit()
        return True

    def update_character_status(self, character_id: int, status: str):
        # Updates a characters' status.
        cur = self.db.execute("UPDATE charlist SET status = ? WHERE charID = ?", (status, character_id))
        self.db.commit()
        return True


db = Database()


def test():
    # Do some automated database testing! :D

    # Test Creating a character with all fields as 'foo' and owner as '1'
    char = character.Character(character_id=0, owner=1, status='foo', name='foo', age='foo', gender='foo', abilities='foo',
                               appearance='foo', species='foo', background='foo', personality='foo', misc='{}')
    character_id = db.create_character(char)
    print(f"Created character with ID: {character_id}")

    # Test getting a character by ID
    del char
    char = db.get_character_by_id(character_id)
    print(f"Got character {char.name} with ID: {char.character_id}")

    # Test modifying a field of character
    char.abilities = 'bar'
    db.update_character(char)
    print(f"Updated char.abilities to {char.abilities}.")

    # Test character deletion.
    db.disable_character(character_id)

    # Prints out a list of all deleted characters
    cur = db.db.execute("SELECT * FROM deleted_chars")
    print(cur.fetchall())


if __name__ == '__main__':
    test()
