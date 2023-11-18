import json
import random
import sqlite3
import os
from helpers import character

import disnake

db_filename = "./config/mttchars.db"


def make_database(file: str):
    schema = open("./schema.sql", "r").read()
    db = sqlite3.connect(file)
    db.executescript(schema)
    db.commit()
    print("Created new database!")


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

    def get_registering_character_by_id(self, character_id: int):
        cur = self.db.execute("SELECT * FROM registering_chars WHERE charID = ?", (character_id,))
        # Converts the character into a character.Character object.
        local_ch = cur.fetchone()
        if local_ch:
            return character.Character(*local_ch[:-1])
        else:
            return None

    def get_registering_thread(self, character_id: int) -> disnake.Thread or None:
        cur = self.db.execute("SELECT thread FROM registering_chars WHERE charID = ?", (character_id,))
        thread = cur.fetchone()
        if thread:
            thread, = thread
        return thread

    # Returns all characters that contain the specified value in the specified field.
    def get_characters_by_search(self, field: str, value: str):
        # let's translate the user fields to what they're called in the bot

        friendly_names = {
            "name": "name",
            "owner": "owner",
            "ownerid": "owner",
            "id": "charID",
            "character id": "charID",
            "charid": "charID",
            "status": "status",
            "age": "age",
            "gender": "gender",
            "sex": "gender",
            "species": "species",
            "abilities": "abilities",
            "abilities/tools": "abilities",
            "tools": "abilities",
            "appearance": "appearance",
            "background": "backstory",
            "backstory": "backstory",
            "personality": "personality",
            "prefilled": "prefilled",
            "prefilled application": "prefilled",
            "misc": "misc",
            "custom": "misc",
            "custom fields": "misc",
        }

        try:
            field = friendly_names[field.lower()]
            cur = self.db.execute(f"SELECT charID, owner, name, status FROM charlist WHERE {field} LIKE ?",
                                  ([f"%{value}%"]))
        except KeyError:
            # invalid key. assume it is incorrect and/or malicious and discard it.
            # searches entire table instead.
            cur = self.db.execute(
                "SELECT charID, owner, name, status FROM charlist WHERE charID LIKE ? OR owner LIKE ? OR status LIKE ? OR name LIKE ? OR age LIKE ? OR gender LIKE ? OR abilities LIKE ? OR appearance LIKE ? OR species LIKE ? OR backstory LIKE ? OR personality LIKE ? OR prefilled LIKE ? OR misc LIKE ?",
                [value, value, value, value, value, value, value, value, value, value, value, value, value])

        # Searches all fields and returns all characters that contain the specified value
        return cur.fetchall()

    # Returns all characters that belong to the specified owner.
    def get_characters_by_owner(self, owner: disnake.Member):
        cur = self.db.execute("SELECT charID, owner, name, status FROM charlist WHERE owner = ?", (owner.id,))
        return cur.fetchall()

    def get_all_characters(self):
        cur = self.db.execute("SELECT charID, owner, name, status FROM charlist")
        return cur.fetchall()

    # Creates a new character from a character.Character object and returns the ID.
    def create_character(self, char: character.Character):

        cur = self.db.execute("INSERT INTO charlist (owner, status, name, age, gender, abilities, appearance, "
                              "species, backstory, personality, prefilled, misc) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                              [char._owner, char._status, char.name, char.age, char.gender, char.abilities,
                               char.appearance, char.species, char.backstory, char.personality, char.prefilled,
                               json.dumps(char.misc)])
        self.db.commit()
        return cur.lastrowid

    # Updates fields of an existing character and returns the ID.
    def update_character(self, char: character.Character):
        js_misc = json.dumps(char.misc)

        cur = self.db.execute(f"UPDATE charlist SET owner = ?, status = ?, name = ?, age = ?, gender = ?, "
                              "abilities = ?, appearance = ?, species = ?, backstory = ?, personality = ?, prefilled "
                              "= ?, misc = ?"
                              "WHERE charID = ?",
                              [char._owner, char._status, char.name, char.age, char.gender, char.abilities,
                               char.appearance, char.species, char.backstory, char.personality, char.prefilled,
                               js_misc, char._character_id])
        self.db.commit()
        return cur.lastrowid

    def update_register_character(self, char: character.Character, thread: disnake.Thread=None):
        js_misc = json.dumps(char.misc)

        if thread:
            cur = self.db.execute(f"UPDATE registering_chars SET owner = ?, status = ?, name = ?, age = ?, gender = ?, "
                              "abilities = ?, appearance = ?, species = ?, backstory = ?, personality = ?, prefilled "
                              "= ?, misc = ?, thread = ? WHERE charID = ?",
                              [char._owner, char._status, char.name, char.age, char.gender, char.abilities,
                               char.appearance, char.species, char.backstory, char.personality, char.prefilled,
                               js_misc, thread.id, char._character_id])
        else:
            cur = self.db.execute(f"UPDATE registering_chars SET owner = ?, status = ?, name = ?, age = ?, gender = ?, "
                              "abilities = ?, appearance = ?, species = ?, backstory = ?, personality = ?, prefilled "
                              "= ?, misc = ? WHERE charID = ?",
                              [char._owner, char._status, char.name, char.age, char.gender, char.abilities,
                               char.appearance, char.species, char.backstory, char.personality, char.prefilled,
                               js_misc, char._character_id])
        self.db.commit()
        return cur.lastrowid

    def finish_character(self, char: character.Character):
        # Finishes a character, moving it to the charlist Table from the registering table.
        # If character exists in charlist, it will be updated. If not, it will be created.
        cur = self.db.execute("SELECT owner FROM charlist WHERE charID = ?", [char._character_id])
        item = cur.fetchone()
        if item:
            item, = item
            if char._owner == item:
                new_id = self.update_character(char)
            else:
                new_id = self.create_character(char)
        else:
            new_id = self.create_character(char)

        # cur = self.db.execute("DELETE FROM registering_chars WHERE charID = ?", [char._character_id])
        self.db.commit()
        return new_id

    def register_character(self, author_id: int, character_id: int | None = None):
        # Gets a character if it exists, else creates a new character with that ID.
        cur = self.db.execute("SELECT * FROM charlist WHERE charID = ?", [character_id])
        char_temp = cur.fetchone()
        if char_temp:
            # Copies the character into registering_chars
            try:
                self.db.execute(
                    "INSERT INTO registering_chars (charID, owner, status, name, age, gender, abilities, appearance, species, backstory, personality, prefilled, misc) SELECT charID, owner, status, name, age, gender, abilities, appearance, species, backstory, personality, prefilled, misc FROM charlist WHERE charID = ?",
                    [character_id])
            except sqlite3.IntegrityError:
                self.update_register_character(db.get_character_by_id(character_id))
            self.db.commit()

            thread = self.db.execute("SELECT thread FROM registering_chars WHERE charID = ?", [character_id]).fetchone()

            return character.Character(*char_temp), thread
        else:
            cur = self.db.execute("SELECT MAX(charID) FROM charlist")
            db_size, = cur.fetchone()
            reg_db_size = self.db.execute("SELECT charID FROM registering_chars").fetchall()

            if not db_size:
                if not reg_db_size:
                    new_id = 1
                else:
                    new_id = reg_db_size[-1][0] + random.randint(10000, 200000)  # last character's ID + a big number
            else:
                new_id = db_size + len(reg_db_size) + random.randint(10000, 200000)

            # Copies the character into registering_chars.
            cur = self.db.execute("INSERT INTO registering_chars (charID, owner, status) VALUES (?, ?, ?)",
                                  [new_id, author_id, "New"])
            self.db.commit()
            character_id = cur.lastrowid
            thread = self.db.execute("SELECT thread FROM registering_chars WHERE charID = ?", [character_id]).fetchone()
            return self.get_registering_character_by_id(character_id), thread

    def disable_character(self, character_id: int):
        # Moves character info to the deleted-chars table.
        cur = self.db.execute("INSERT INTO deleted_chars SELECT * FROM charlist WHERE charID = ?", (character_id,))
        cur = self.db.execute("DELETE FROM charlist WHERE charID = ?", (character_id,))
        self.db.commit()
        return True

    def delete_registering_character(self, character_id: int):
        # Moves character info to the deleted-chars table.
        self.db.execute("DELETE FROM registering_chars WHERE charID = ?", (character_id,))
        self.db.commit()
        return True

    def update_character_status(self, character_id: int, status: str):
        # Updates a characters' status.
        cur = self.db.execute("UPDATE charlist SET status = ? WHERE charID = ?", (status, character_id))

        self.db.execute("DELETE FROM registering_chars WHERE charID = ?", [character_id])

        self.db.commit()
        if not cur.rowcount:
            return False
        return True

    def get_votes(self, character_id):
        cur = self.db.execute("SELECT for_votes, against_votes FROM character_votes WHERE charID = ?", (character_id,))
        return cur.fetchone()

    def clear_votes(self, character_id: int = None):
        cur = self.db.execute("DELETE FROM character_votes WHERE charID = ?", (character_id,))
        self.db.commit()
        return True

    def add_vote(self, character_id: int = None, positive: int = None, negative: int = None, author: int = None):

        votes = self.get_votes(character_id=character_id)
        if votes:
            positive_votes = votes[0].split(',')
            if positive_votes[0] == '':
                positive_votes = []
            negative_votes = votes[1].split(',')
            if negative_votes[0] == '':
                negative_votes = []
            new_row = False
        else:
            positive_votes = []
            negative_votes = []
            new_row = True

        if positive:
            if str(author) in negative_votes:
                negative_votes.remove(str(author))
            if str(author) not in positive_votes:
                positive_votes.append(str(author))
        elif negative:
            if str(author) in positive_votes:
                positive_votes.remove(str(author))
            if str(author) not in negative_votes:
                negative_votes.append(str(author))
        else:
            return False

        new_positive = ','.join(positive_votes)
        new_negative = ','.join(negative_votes)

        if new_row:
            self.db.execute("INSERT INTO character_votes (charID, for_votes, against_votes) VALUES (?, ?, ?)",
                            (character_id, new_positive, new_negative))
        else:
            self.db.execute("UPDATE character_votes SET for_votes = ?, against_votes = ? WHERE charID = ?",
                            (new_positive, new_negative, character_id))
        self.db.commit()
        return True


db = Database()


def convert(): # use this to convert mtt2.0 databases to mtt3.0 databases
    # rename the db to oldmttchars.db
    old_db = sqlite3.connect('./config/oldmttchars.db')

    src_cur = old_db.cursor()
    dest_cur = db.db.cursor()


    src_cur.execute("SELECT * FROM charlist")

    for row in src_cur.fetchall():
        dest_cur.execute("INSERT INTO charlist VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", row)
    db.db.commit()
    dest_cur.execute("INSERT INTO deleted_chars SELECT * FROM charlist WHERE status = 'Disabled'")
    db.db.commit()
    dest_cur.execute("DELETE FROM charlist WHERE status = 'Disabled'")
    db.db.commit()
    old_db.close()

if __name__ == '__main__':
    convert()

# to do before this goes live:

# move all deleted chars from main DB
#  INSERT INTO deleted_chars SELECT * FROM charlist WHERE status = 'Disabled'
#  DELETE FROM charlist WHERE status = 'Disabled'
