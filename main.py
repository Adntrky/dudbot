import os
import discord
from discord.ext import commands

import config


__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

description = "A bot to make a dude feel cosy."
bot = commands.Bot(command_prefix=commands.when_mentioned_or('['), description=description)
bot.remove_command("help")

cogs = ['extensions.utility', 'extensions.music', 'extensions.image_search', 'extensions.reddit']

bot_token = config.bot_token
filter_file = open(os.path.join(__location__, 'chat_filter.txt'))
filter_is_enabled = True
chat_filter = filter_file.read().split('\n')


if not discord.opus.is_loaded():
    discord.opus.load_opus(os.path.join(__location__, '\lib\opus.dll'))


@bot.event
async def on_ready():
    servers = list(bot.servers)
    await bot.change_presence(game=discord.Game(name='[help'))
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


@bot.event
async def on_message(message):
    if filter_is_enabled:
        for x in chat_filter:
            if x in message.content.lower():
                em = discord.Embed(title='YOU DONE GOOFED', description='\u200b', colour=0xFF0000)
                em.set_image(url="https://hypixel.net/proxy/aHR0cDovL2kwLmt5bS1jZG4uY29tL3Bob3Rvcy9pbWFnZXMvbmV3c2ZlZWQvMDAxLzI5OS8zODYvYTI2LmpwZWc%3D/image.png")
                await bot.send_message(message.channel, embed=em)
                break
    if (message.server.name == "Such Server! Wow" and message.author.top_role.name == "Doge") or message.server.name != "Such Server! Wow":
        await bot.process_commands(message)
    return


@bot.command(pass_context=True)
async def tf(self):
    global filter_is_enabled
    filter_is_enabled = not filter_is_enabled
    if filter_is_enabled:
        await self.bot.say('Chat filter enabled.')
    else:
        await self.bot.say('Chat filter disabled.')


if __name__ == '__main__':
    for cog in cogs:
        try:
            bot.load_extension(cog)
        except Exception as error:
            print('\n{} cannot be loaded. [{}]\n'.format(cog, error))
    bot.run(bot_token)
