import requests
from discord.ext import commands

from config import cleverbot


class Cleverbot:

    is_enabled = False

    def __init__(self, bot):
        self.bot = bot

    async def on_message(self, message):
        payload = {'user': cleverbot['api_user'], 'key': cleverbot['api_key'], 'nick': 'dudbot', 'text':message.content}
        if not message.author.bot and Cleverbot.is_enabled and not message.content.startswith(']'):
            session = requests.Session()
            # session.trust_env = False
            with session.post('https://cleverbot.io/1.0/ask', data=payload) as r:
                data = r.json()
                await self.bot.send_message(message.channel, data['response'])

    @commands.command(pass_context=True)
    async def tc(self):
        Cleverbot.is_enabled = not Cleverbot.is_enabled
        if Cleverbot.is_enabled:
            await self.bot.say('What\'s up?')
        else:
            await self.bot.say('Cya.')


def setup(bot):
    bot.add_cog(Cleverbot(bot))
