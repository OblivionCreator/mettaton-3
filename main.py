import os

import disnake
from disnake.ext.commands import Bot

bot = Bot(command_prefix='.', intents=disnake.Intents().all())

if __name__ == '__main__':
    for file in os.listdir('modules'):
        if file.endswith('.py'):
            bot.load_extension(f'modules.{file.split(".")[0]}')

@bot.slash_command(name='reload_all_modules')
async def reload_all_modules(inter):
    os.system('git pull origin master')

    for file in os.listdir('modules'):
        if file.endswith('.py'):
            bot.reload_extension(f'modules.{file.split(".")[0]}')
    await inter.send('Reloaded all modules.')

bot.run(open('./config/token.txt').read())