import disnake
from disnake.ext import commands
from helpers import character, database, config

db = database.Database()
conf = config.Config()


class Set(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.write_required = True

    @commands.slash_command()
    async def set(self, inter: disnake.ApplicationCommandInteraction, character_id: int, field: str, value: str):
        char = db.get_character_by_id(character_id)

        if not char:
            await inter.send("Character with ID {} was not found!".format(character_id), ephemeral=True)
            return

        if not isinstance(char._character_id, int):  # something's gone fucky, so we're just gonna check GM role here
            if inter.guild.get_role(conf.gamemaster_role) not in inter.author.roles:
                await inter.send(
                    "Something has gone wrong with this character and one of the fields is corrupted. Please contact a GM!")
                return
        elif not inter.author.id == int(char._owner) and inter.guild.get_role(
                conf.gamemaster_role) not in inter.author.roles:
            await inter.send("You do not own this character!", ephemeral=True)
            return

        embed = disnake.Embed()


        if field.lower() in vars(char).keys():

            if (field.lower().startswith('_') or f'_{field.lower()}' in vars(char).keys()) and inter.guild.get_role(conf.gamemaster_role) not in inter.author.roles:
                await inter.send("You can not edit this field!", ephemeral=True)
                return

            if f'_{field}' in vars(char):
                field = '_' + field.lower()

            if value.lower().strip() == 'delete':
                await inter.send("You can not delete this field!", ephemeral=True)
                return

            old_embed = char.get_field_view(character_id, field)
            setattr(char, field.lower(), value)
            db.update_character(char)
            new_embed = char.get_field_view(character_id, field)

            await self.log_change(inter, old_embed, new_embed, field, character_id)

            embed.title = f"Field {field} has been changed."
            embed.description = value
            await inter.send(embed=embed)
            return
        else:

            # hacky way of handling preset custom fields
            if field.lower() == 'portrait':
                field = 'Portrait'

            if field.lower() == 'mrc':
                field = 'MRC'

            # field does not exist, add to custom fields.
            # deletes existing fields.
            if value.lower().strip() == 'delete':
                for key in char.misc.keys():
                    if key == field:
                        old_embed = char.get_field_view(character_id, field)
                        char.misc.pop(key)
                        db.update_character(char)
                        await inter.send(f"Custom Field {field} has been deleted.")
                        new_embed = disnake.Embed(title=f"Viewing field {field} for ID {character_id}", description="Field was deleted.")
                        await self.log_change(inter, old_embed, new_embed, field, character_id)
                        return
                await inter.send(f"Field {field} was not found! Please note that custom fields are CaSe SeNsItIvE!")
                return

            success = False

            # add new field

            embed.title = f"Field {field} has been changed."
            embed.description = value

            for key in char.misc.keys():
                if key.lower() == field.lower():
                    old_embed = char.get_field_view(character_id, field)
                    char.misc[key] = value
                    db.update_character(char)
                    success = True
                    break

            if not success:
                old_embed = disnake.Embed(title="New Field", description="No old version of this field is available!")
                char.misc[field] = value
                db.update_character(char)

            new_embed = char.get_field_view(character_id, field)
            await self.log_change(inter, old_embed, new_embed, field, character_id)
            await inter.send(embed=embed, ephemeral=True)


    async def log_change(self, inter, old_embed:disnake.Embed, new_embed, field, character_id):
        old_embed.title = f"Original Value of '{field}'"
        new_embed.title = f"New Value of '{field}'"

        log_channel = inter.guild.get_channel(conf.log_channel)
        if log_channel:
            await log_channel.send(
            f"{inter.author.name} ({inter.author.id}) changed Field {field} for Character ID {character_id}",
            embeds=[old_embed, new_embed])

def setup(bot):
    bot.add_cog(Set(bot))
