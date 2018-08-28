import random
import discord
from discord.ext import commands


class Utility:
    def __init__(self, bot):
        self.bot = bot

    @commands.group(pass_context=True)
    async def help(self):
        em = discord.Embed(title="Commands:", description="A bot to make a dud feel cosy.", color=0x3498DB)
        em.add_field(name="--------------------------------------------------------------------------------", value="\u200b", inline=True)
        em.add_field(name="Utility", value="Displays all utility commands. Usage: ]help utility", inline=True)
        em.add_field(name="Music", value="Displays all music commands. Usage: ]help music", inline=True)
        em.add_field(name="Image Search", value="Displays all image related commands. Usage: ]help image", inline=True)
        em.set_thumbnail(url=self.bot.user.avatar_url)
        await self.bot.say(embed=em)

    @help.command(pass_context=True)
    async def utility(self):
        em = discord.Embed(title="Utility Commands:", description="Helpful tools to make a dud feel cosy.", color=0x3498DB)
        em.add_field(name="--------------------------------------------------------------------------------", value="\u200b", inline=True)
        em.add_field(name="dud", value="Check if the bot is operational.", inline=True)
        em.add_field(name="add", value="Adds two numbers together. Usage: ]add 5 7", inline=True)
        em.add_field(name="roll", value="Rolls die. Usage: ]roll (number of die)d(number of sides)", inline=True)
        em.add_field(name="choose", value="Choose between options. Usage: ]choose cat dog", inline=True)
        em.add_field(name="tf", value="Stands for \"toggle filter\". Toggles chat filter on/off.", inline=True)
        em.add_field(name="info", value="Gives information about the user.", inline=False)
        em.add_field(name="serverinfo", value="Gives information about the server.", inline=False)
        em.set_thumbnail(url=self.bot.user.avatar_url)
        await self.bot.say(embed=em)

    @help.command(pass_context=True)
    async def music(self):
        em = discord.Embed(title="Music Commands:", description="Music to make a dud feel cosy.", color=0x3498DB)
        em.add_field(name="--------------------------------------------------------------------------------", value="\u200b", inline=True)
        em.add_field(name="play", value="Plays an audio file from the internet. Usage: ]play (video url)", inline=True)
        em.add_field(name="summon", value="Bot joins the voice channel the user is in.", inline=True)
        em.add_field(name="join", value="Bot joins the specified voice channel. Usage: ]join (channel name)", inline=True)
        em.add_field(name="stop", value="Stops playing audio and leaves the voice channel. Deletes the queue.", inline=True)
        em.add_field(name="volume", value="Changes audio volume. Usage: ]volume (number)", inline=True)
        em.add_field(name="pause", value="Pauses the audio file.", inline=True)
        em.add_field(name="resume", value="Resumes playing the audio file.", inline=False)
        em.add_field(name="skip", value="Skips the audio file and plays the next one in the queue.", inline=True)
        em.add_field(name="playing", value="Displays currently playing audio.", inline=True)
        em.set_thumbnail(url=self.bot.user.avatar_url)
        await self.bot.say(embed=em)

    @help.command(pass_context=True)
    async def image(self):
        em = discord.Embed(title="Image Search Commands:", description="Images to make a dud feel cosy.", color=0x3498DB)
        em.add_field(name="--------------------------------------------------------------------------------", value="\u200b", inline=True)
        em.add_field(name="reddit", value="Gets a random picture of the last 50 posts of the hot page from the subreddit provided. Usage: ]reddit pic <subreddit>", inline=True)
        em.add_field(name="----------------------------------------", value="The commands below are reverse image search commands and can be used in image upload comment.", inline=True)
        em.add_field(name="iqdb", value="Search IQDB for source of an image on danbooru. Usage: ]iqdb <image_link>", inline=True)
        em.add_field(name="sauce", value="Reverse image search on saucenao. Usage: ]sauce <image_link>", inline=True)
        em.add_field(name="tineye", value="Reverse image search on tineye. Usage: ]tineye <image_link>", inline=True)
        em.set_thumbnail(url=self.bot.user.avatar_url)
        await self.bot.say(embed=em)

    @commands.command()
    async def dud(self):
        """Checks if the bot is operational."""
        await self.bot.say('Yo')

    @commands.command()
    async def add(self, left: int, right: int):
        """Adds two numbers together."""
        await self.bot.say(left + right)

    @commands.command()
    async def roll(self, dice: str):
        """Rolls a dice in NdN format."""
        try:
            rolls, limit = map(int, dice.split('d'))
        except Exception:
            await self.bot.say('Format has to be in NdN!')
            return

        result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
        await self.bot.say(result)

    @commands.command(description='For when you wanna settle the score some other way')
    async def choose(self, *choices: str):
        """Chooses between multiple choices."""
        await self.bot.say(random.choice(choices))

    @commands.command()
    async def repeat(self, times: int, content='repeating'):
        """Repeats a message multiple times."""
        if times <= 5:
            for i in range(times):
                await self.bot.say(content)
        else:
            await self.bot.say('No.')

    @commands.command()
    async def joined(self, member: discord.Member):
        """Says when a member joined."""
        await self.bot.say('{0.name} joined in {0.joined_at}'.format(member))

    @commands.command(pass_context=True)
    async def info(self, ctx):
        user = ctx.message.author
        embed = discord.Embed(title="{}'s info".format(user.name), description="Here's what I could find.", color=0x3498DB)
        embed.add_field(name="Name", value=user.name, inline=True)
        embed.add_field(name="ID", value=user.id, inline=True)
        embed.add_field(name="Status", value=user.status, inline=True)
        embed.add_field(name="Highest role", value=user.top_role)
        embed.add_field(name="Joined", value=user.joined_at)
        embed.set_thumbnail(url=user.avatar_url)
        await self.bot.say(embed=embed)

    @commands.command(pass_context=True)
    async def serverinfo(self, ctx):
        embed = discord.Embed(name="{}'s info".format(ctx.message.server.name), description="Here's what I could find.", color=0x3498DB)
        embed.add_field(name="Name", value=ctx.message.server.name, inline=True)
        embed.add_field(name="ID", value=ctx.message.server.id, inline=True)
        embed.add_field(name="Roles", value="{}".format(len(ctx.message.server.roles)), inline=True)
        embed.add_field(name="Members", value="{}".format(len(ctx.message.server.members)))
        embed.set_thumbnail(url=ctx.message.server.icon_url)
        await self.bot.say(embed=embed)

    @commands.command(pass_context=True)
    async def checkopus(self):
        if discord.opus.is_loaded():
            await self.bot.say("Opus shared library is lock & loaded.")

    @commands.command(pass_context=True)
    async def niceu(self):
        em = discord.Embed(title='VERY NICEU CAESAR-KUN', description='\u200b', colour=0xDEADBF)
        em.set_image(url="https://i.ytimg.com/vi/ffQmb-cNFuk/maxresdefault.jpg")
        await self.bot.say(embed=em)

    @commands.command(pass_context=True)
    async def clean(self, ctx, number=None):
        mgs = []
        if number is None:
            number = 100
        number = int(number)
        async for x in self.bot.logs_from(ctx.message.channel, limit=number):
            if ctx.message.author == x.author:
                mgs.append(x)
        await self.bot.delete_messages(mgs)


def setup(bot):
    bot.add_cog(Utility(bot))
