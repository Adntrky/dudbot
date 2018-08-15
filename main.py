import os
import discord
from discord.ext import commands

import config


__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

description = "A bot to make a dude feel cosy."
bot = commands.Bot(command_prefix=commands.when_mentioned_or(']'), description=description)
bot_token = config.bot_token

cogs = ['extensions.utility', 'extensions.music', 'extensions.image_search', 'extensions.reddit', 'extensions.filter']

bot.remove_command("help")


if not discord.opus.is_loaded():
    discord.opus.load_opus(os.path.join(__location__, '\lib\opus.dll'))


@bot.event
async def on_ready():
    servers = list(bot.servers)
    await bot.change_presence(game=discord.Game(name=']help'))
    print('Logged in as:')
    print(bot.user.name)
    print(bot.user.id)
    if len(bot.servers) > 1:
        plural = "s"
    else:
        plural = ""
    print('---------------------------')
    print("Connected on {} server{}.".format(str(len(bot.servers)), plural) + ' ')
    for x in range(len(servers)):
        print(' ' + servers[x-1].name)
    print('---------------------------')


if __name__ == '__main__':
    for cog in cogs:
        try:
            bot.load_extension(cog)
        except Exception as error:
            print('\n{} cannot be loaded. [{}]\n'.format(cog, error))
    bot.run(bot_token)
