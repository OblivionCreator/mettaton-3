import os

import disnake
from disnake.ext.commands import Bot

intents = disnake.Intents().all()

bot = Bot(command_prefix='.', intents=intents)

if __name__ == '__main__':
    for file in os.listdir('modules'):
        if file.endswith('.py'):
            bot.load_extension(f'modules.{file.split(".")[0]}')

bot.run(open('./config/token.txt').read())
