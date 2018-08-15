import os
import discord
from discord.ext import commands
from main import __location__


filter_file = open(os.path.join(__location__, 'chat_filter.txt'))
chat_filter = filter_file.read().split('\n')


class Filter:
    
    is_enabled = True
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def tf(self):
        self.is_enabled = not self.is_enabled
        if self.is_enabled:
            await self.bot.say('Chat filter enabled.')
        else:
            await self.bot.say('Chat filter disabled.')

    async def on_message(self, message):
        if self.is_enabled:
            for x in chat_filter:
                if x in message.content.lower():
                    em = discord.Embed(title='YOU DONE GOOFED', description='\u200b', colour=0xFF0000)
                    em.set_image(url="https://hypixel.net/proxy/aHR0cDovL2kwLmt5bS1jZG4uY29tL3Bob3Rvcy9pbWFnZXMvbmV3c2ZlZWQvMDAxLzI5OS8zODYvYTI2LmpwZWc%3D/image.png")
                    await self.bot.send_message(message.channel, embed=em)
                    break


def setup(bot):
    bot.add_cog(Filter(bot))
