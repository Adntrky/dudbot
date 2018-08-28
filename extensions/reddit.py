import os
import asyncio
import praw
import discord
from discord.ext import commands
from random import randint

from config import reddit
from main import __location__


reddit_icon = 'https://camo.githubusercontent.com/b13830f5a9baecd3d83ef5cae4d5107d25cdbfbe/68747470733a2f2f662e636c6f75642e6769746875622e636f6d2f6173736574732f3732313033382f313732383830352f35336532613364382d363262352d313165332d383964312d3934376632373062646430332e706e67'
reddit = praw.Reddit(client_id=reddit['client_id'], client_secret=reddit['client_secret'], password=reddit['password'], user_agent=reddit['user_agent'], username=reddit['username'])
duplicate_filter_file = open(os.path.join(__location__, 'duplicate_image_filter.txt'))  # TODO find and apply the best way to read and write the duplicate_filter_file
duplicate_filter = duplicate_filter_file.read().split('\n')


class Reddit:

    is_auto = False

    def __init__(self, bot):
        self.bot = bot

    @commands.group(pass_context=True)
    async def reddit(self, ctx):
        if ctx.invoked_subcommand is None:
            await self.bot.say('That command does not exist in this group')

    @reddit.command(pass_context=True)
    async def pic(self, ctx, sub: str):
                try:
                    submissions = list(reddit.subreddit(sub).hot(limit=100))
                except:
                    return await self.bot.say('Subreddit not found')

                if len(submissions) == 0:
                    return await self.bot.say('Not any images on this sub')

                rand = randint(0, 99) if len(submissions) >= 100 else randint(0, len(submissions))
                picture = submissions[rand].url
                while 'imgur.com/a/' in picture or 'reddit.com/r/' in picture:
                    rand = randint(0, 99) if len(submissions) >= 100 else randint(0, len(submissions))
                    picture = submissions[rand].url

                if 'jpg' not in picture and 'png' not in picture:
                    picture += '.jpg'

                print(picture)

                for x in duplicate_filter:
                    if str(picture) in str(x):
                        with open(os.path.join(__location__, 'duplicate_image_filter.txt'), 'a') as data:
                            data.write(picture + '\n')
                        await self.bot.say(embed=discord.Embed().set_image(url=picture).set_footer(text=sub, icon_url=reddit_icon))
                        break
                    else:
                        print('Image already in database. [{}]'.format(picture))

    @reddit.command(pass_context=True)
    async def ao(self):
        self.is_auto = False
        await self.bot.say('Auto posting disabled.')

    @reddit.command(pass_context=True)
    async def auto(self, ctx, sub: str, interval: int):
        self.is_auto = True
        while self.is_auto is True:
            try:
                submissions = list(reddit.subreddit(sub).hot(limit=100))
            except:
                return await self.bot.say('Subreddit not found')

            if len(submissions) == 0:
                return await self.bot.say('Not any images on this sub')

            rand = randint(0, 99) if len(submissions) >= 100 else randint(0, len(submissions))
            picture = submissions[rand].url
            while 'imgur.com/a/' in picture or 'reddit.com/r/' in picture:
                rand = randint(0, 99) if len(submissions) >= 100 else randint(0, len(submissions))
                picture = submissions[rand].url

            if 'jpg' not in picture and 'png' not in picture:
                picture += '.jpg'

            for x in duplicate_filter:
                if picture not in x:
                    duplicate_filter_file.close()
                    with open(os.path.join(__location__, 'duplicate_image_filter.txt'), 'a') as data:
                        data.write(picture + '\n')
                    await self.bot.say(embed=discord.Embed().set_image(url=picture).set_footer(text=sub, icon_url=reddit_icon))
                    await asyncio.sleep(interval * 60)
                    break
                else:
                    print('Image already in database. [{}]'.format(picture))
                    await asyncio.sleep(10)
                    break


def setup(bot):
    bot.add_cog(Reddit(bot))
