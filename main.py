import os

import disnake
from disnake.ext.commands import Bot
from helpers import config

intents = disnake.Intents().all()
conf = config.Config()

bot = Bot(command_prefix='.', intents=intents)

if __name__ == '__main__':

    for file in os.listdir('modules'):
        if file.endswith('.py'):
            bot.load_extension(f'modules.{file.split(".")[0]}')

    if not conf.read_only:
        for file in os.listdir('modules/write-required'):
            if file.endswith('.py'):
                bot.load_extension(f'modules.write-required.{file.split(".")[0]}')

bot.run(open('./config/token.txt').read())
