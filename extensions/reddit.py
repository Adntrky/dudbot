import praw
import discord
from discord.ext import commands
from random import randint

from config import reddit


reddit_icon = 'https://camo.githubusercontent.com/b13830f5a9baecd3d83ef5cae4d5107d25cdbfbe/68747470733a2f2f662e636c6f75642e6769746875622e636f6d2f6173736574732f3732313033382f313732383830352f35336532613364382d363262352d313165332d383964312d3934376632373062646430332e706e67'
reddit = praw.Reddit(client_id=reddit['client_id'], client_secret=reddit['client_secret'], password=reddit['password'], user_agent=reddit['user_agent'], username=reddit['username'])


class Reddit:
    def __init__(self, bot):
        self.bot = bot

    @commands.group(pass_context=True)
    async def reddit(self, ctx):
        if ctx.invoked_subcommand is None:
            await self.bot.say('That command does not exist in this group')

    @reddit.command(pass_context=True)
    async def pic(self, ctx, sub: str):
        try:
            submissions = list(reddit.subreddit(sub).hot(limit=50))
        except:
            return await self.bot.say('Subreddit not found')

        if len(submissions) == 0:
            return await self.bot.say('Not any images on this sub')

        rand = randint(0, 49) if len(submissions) >= 50 else randint(0, len(submissions))
        picture = submissions[rand].url
        while 'imgur.com/a/' in picture or 'reddit.com/r/' in picture:
            rand = randint(0, 49) if len(submissions) >= 50 else randint(0, len(submissions))
            picture = submissions[rand].url

        if 'jpg' not in picture and 'png' not in picture:
            picture += '.jpg'

        print(picture)
        await self.bot.say(embed=discord.Embed().set_image(url=picture).set_footer(text=sub, icon_url=reddit_icon))


def setup(bot):
    bot.add_cog(Reddit(bot))
