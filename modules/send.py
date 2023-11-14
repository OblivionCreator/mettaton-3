import disnake
import validators
from disnake.ext import commands
from helpers import character, database, config, webhook_manager

db = database.Database()
conf = config.Config()


class Send(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_message")
    async def send(self, ctx: disnake.Message):
        if ctx.author.bot:
            return

        if not ctx.content.startswith("$"):
            return

        # it is now a valid $send command
        # should be formatted in either:
        # $charname:message
        # or
        # $charid:message

        split_data = ctx.content.split(":")

        if len(split_data) < 2:
            return
        if len(split_data) > 2:
            message = ":".join(split_data[1:])
        # if someone does $sdfdfhudf without a colon, returns
        # else it merges all past the first colon into the message, to prevent it causing issues.

        raw_character = split_data[0].strip('$')
        message = split_data[1].strip()

        character_data = None

        if raw_character.isnumeric():
            character_id = int(raw_character)
            character_data = db.get_character_by_id(character_id)
            if character_data is None:
                await ctx.message.delete()
                try:
                    await ctx.author.send("Send command failed as the bot was unable to find any characters with that name.\nMessage:\n" + ctx.content)

                except:
                    pass
                return
        else:
            char_list = db.get_characters_by_search('name', raw_character)
            if len(char_list) == 0:
                await ctx.message.delete()
                try:
                    await ctx.author.send("Send command failed as the bot was unable to find any characters with that name.\nMessage:\n" + ctx.content)
                except:
                    pass
                return
            for char in char_list:
                if int(char[1]) == ctx.author.id:
                    character_data = db.get_character_by_id(char[0])
                    break

        if not character_data:
            await ctx.message.delete()
            try:
                await ctx.author.send("Send command failed as the bot was unable to find any characters with that name.\nMessage:\n" + ctx.content)
            except:
                pass
            return

        if message == '':
            await ctx.message.delete()
            try:
                await ctx.author.send("Send command failed as the message was empty!\nMessage:\n" + ctx.content)
            except:
                pass
            return

        # got the name, message, time to send a webhook!
        image = None
        # check for portrait field
        for key in character_data.misc.keys():
            if key.lower() == 'portrait':
                # validate it resembles a url
                if validators.url(character_data.misc[key]):
                    image = character_data.misc[key]
                break

        await webhook_manager.send(ctx, character_data.name[0:80], message, image)


def setup(bot):
    bot.add_cog(Send(bot))
