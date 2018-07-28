import asyncio
import discord
from discord.ext import commands
import random
import os

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

if not discord.opus.is_loaded():
    discord.opus.load_opus(os.path.join(__location__, '\lib\opus.dll'))


class VoiceEntry:
    def __init__(self, message, player):
        self.requester = message.author
        self.channel = message.channel
        self.player = player

    def __str__(self):
        fmt = '*{0.title}* uploaded by {0.uploader} and requested by {1.display_name}'
        duration = self.player.duration
        if duration:
            fmt = fmt + ' [length: {0[0]}m {0[1]}s]'.format(divmod(duration, 60))
        return fmt.format(self.player, self.requester)


class VoiceState:
    def __init__(self, bot):
        self.current = None
        self.voice = None
        self.bot = bot
        self.play_next_song = asyncio.Event()
        self.songs = asyncio.Queue()
        self.skip_votes = set()  # a set of user_ids that voted
        self.audio_player = self.bot.loop.create_task(self.audio_player_task())

    def is_playing(self):
        if self.voice is None or self.current is None:
            return False

        player = self.current.player
        return not player.is_done()

    @property
    def player(self):
        return self.current.player

    def skip(self):
        self.skip_votes.clear()
        if self.is_playing():
            self.player.stop()

    def toggle_next(self):
        self.bot.loop.call_soon_threadsafe(self.play_next_song.set)

    async def audio_player_task(self):
        while True:
            self.play_next_song.clear()
            self.current = await self.songs.get()
            await self.bot.send_message(self.current.channel, 'Now playing ' + str(self.current))
            self.current.player.start()
            await self.play_next_song.wait()


class Music:
    """Voice related commands."""
    def __init__(self, bot):
        self.bot = bot
        self.voice_states = {}

    def get_voice_state(self, server):
        state = self.voice_states.get(server.id)
        if state is None:
            state = VoiceState(self.bot)
            self.voice_states[server.id] = state

        return state

    async def create_voice_client(self, channel):
        voice = await self.bot.join_voice_channel(channel)
        state = self.get_voice_state(channel.server)
        state.voice = voice

    def __unload(self):
        for state in self.voice_states.values():
            try:
                state.audio_player.cancel()
                if state.voice:
                    self.bot.loop.create_task(state.voice.disconnect())
            except:
                pass

    @commands.command(pass_context=True, no_pm=True)
    async def join(self, ctx, *, channel: discord.Channel):
        try:
            await self.create_voice_client(channel)
        except ValueError:
            await self.bot.say('Please enter a voice channel')
        except discord.InvalidArgument:
            await self.bot.say('This is not a voice channel')
        except discord.ClientException:
            await self.bot.say('Already in a voice channel')
        else:
            await self.bot.say('Ready to play audio in {}'.format(channel.name))

    @commands.command(pass_context=True, no_pm=True)
    async def leave(self, ctx):
        server = ctx.message.server
        state = self.get_voice_state(server)

        if state.is_playing():
            player = state.player
            player.stop()

        try:
            state.audio_player.cancel()
            del self.voice_states[server.id]
            await state.voice.disconnect()
        except:
            pass

    @commands.command(pass_context=True, no_pm=True)
    async def summon(self, ctx):
        summoned_channel = ctx.message.author.voice_channel
        if summoned_channel is None:
            await self.bot.say('You are not in a voice channel.')
            return False

        state = self.get_voice_state(ctx.message.server)
        if state.voice is None:
            state.voice = await self.bot.join_voice_channel(summoned_channel)
        else:
            await state.voice.move_to(summoned_channel)

        return True

    @commands.command(pass_context=True, no_pm=True)
    async def play(self, ctx, *, song: str):
        """The list of supported sites: https://rg3.github.io/youtube-dl/supportedsites.html"""
        for x in voice_filter:
            if x in song.lower():
                await self.bot.say("No.")
                return

        state = self.get_voice_state(ctx.message.server)
        opts = {
            'default_search': 'auto',
            'quiet': True,
        }

        if state.voice is None:
            success = await ctx.invoke(self.summon)
            if not success:
                return

        try:
            player = await state.voice.create_ytdl_player(song, ytdl_options=opts, after=state.toggle_next)
        except Exception as e:
            fmt = 'An error occurred while processing this request: ```py\n{}: {}\n```'
            await self.bot.send_message(ctx.message.channel, fmt.format(type(e).__name__, e))
        else:
            player.volume = 0.6
            entry = VoiceEntry(ctx.message, player)
            await self.bot.say('Enqueued ' + str(entry))
            await state.songs.put(entry)

    @commands.command(pass_context=True, no_pm=True)
    async def deltree(self, ctx):
        state = self.get_voice_state(ctx.message.server)
        opts = {
            'default_search': 'auto',
            'quiet': True,
        }

        if state.voice is None:
            success = await ctx.invoke(self.summon)
            if not success:
                return

        try:
            player = await state.voice.create_ytdl_player("https://www.youtube.com/watch?v=6uI_hNdj4UE", ytdl_options=opts, after=state.toggle_next)
        except Exception as e:
            fmt = 'An error occurred while processing this request: ```py\n{}: {}\n```'
            await self.bot.send_message(ctx.message.channel, fmt.format(type(e).__name__, e))
        else:
            player.volume = 0.6
            entry = VoiceEntry(ctx.message, player)
            await self.bot.say('Enqueued ' + str(entry))
            await state.songs.put(entry)

    @commands.command(pass_context=True, no_pm=True)
    async def volume(self, ctx, value: int):
        state = self.get_voice_state(ctx.message.server)
        if state.is_playing():
            player = state.player
            player.volume = value / 100
            await self.bot.say('Set the volume to {:.0%}'.format(player.volume))

    @commands.command(pass_context=True, no_pm=True)
    async def pause(self, ctx):
        state = self.get_voice_state(ctx.message.server)
        if state.is_playing():
            player = state.player
            player.pause()

    @commands.command(pass_context=True, no_pm=True)
    async def resume(self, ctx):
        state = self.get_voice_state(ctx.message.server)
        if state.is_playing():
            player = state.player
            player.resume()

    @commands.command(pass_context=True, no_pm=True)
    async def stop(self, ctx):
        server = ctx.message.server
        state = self.get_voice_state(server)

        if state.is_playing():
            player = state.player
            player.stop()

        try:
            state.audio_player.cancel()
            del self.voice_states[server.id]
            await state.voice.disconnect()
        except:
            pass

    @commands.command(pass_context=True, no_pm=True)
    async def skip(self, ctx):
        state = self.get_voice_state(ctx.message.server)
        if not state.is_playing():
            await self.bot.say('Not playing any music right now')
            return

        voter = ctx.message.author
        if voter == state.current.requester:
            await self.bot.say('Requester requested skipping song')
            state.skip()
        elif voter.id not in state.skip_votes:
            state.skip_votes.add(voter.id)
            total_votes = len(state.skip_votes)
            if total_votes >= 3:
                await self.bot.say('Skip vote passed, skipping song')
                state.skip()
            else:
                await self.bot.say('Skip vote added, currently at [{}/3]'.format(total_votes))
        else:
            await self.bot.say('You have already voted to skip this song.')

    @commands.command(pass_context=True, no_pm=True)
    async def playing(self, ctx):
        state = self.get_voice_state(ctx.message.server)
        if state.current is None:
            await self.bot.say('Not playing anything.')
        else:
            skip_count = len(state.skip_votes)
            await self.bot.say('Now playing {} [skips: {}/3]'.format(state.current, skip_count))


description = "A bot to make a dude feel cosy."
bot = commands.Bot(command_prefix=commands.when_mentioned_or(']'), description=description)
bot_token_file = open(os.path.join(__location__, 'bot_token.txt'))
filter_file = open(os.path.join(__location__, 'chat_filter.txt'))
filter_is_enabled = True
chat_filter = filter_file.read().split('\n')
voice_filter = ('despacito', 'ですぱしと', 'カタカナ')
bot.remove_command("help")
bot.add_cog(Music(bot))


@bot.event
async def on_ready():
    await bot.change_presence(game=discord.Game(name=']help'))
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


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


'''There are a number of utility commands being showcased here.'''


@bot.command(pass_context=True)
async def tf():
    global filter_is_enabled
    filter_is_enabled = not filter_is_enabled
    if filter_is_enabled:
        await bot.say('Chat filter enabled.')
    else:
        await bot.say('Chat filter disabled.')


@bot.command()
async def dud():
    """Checks if the bot is operational."""
    await bot.say('Yo')


@bot.command()
async def add(left: int, right: int):
    """Adds two numbers together."""
    await bot.say(left + right)


@bot.command()
async def roll(dice: str):
    """Rolls a dice in NdN format."""
    try:
        rolls, limit = map(int, dice.split('d'))
    except Exception:
        await bot.say('Format has to be in NdN!')
        return

    result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
    await bot.say(result)


@bot.command(description='For when you wanna settle the score some other way')
async def choose(*choices: str):
    """Chooses between multiple choices."""
    await bot.say(random.choice(choices))


@bot.command()
async def repeat(times: int, content='repeating'):
    """Repeats a message multiple times."""
    if times <= 5:
        for i in range(times):
            await bot.say(content)
    else:
        await bot.say('No.')


@bot.command()
async def joined(member: discord.Member):
    """Says when a member joined."""
    await bot.say('{0.name} joined in {0.joined_at}'.format(member))


@bot.command(pass_context=True)
async def info(ctx):
    user = ctx.message.author
    embed = discord.Embed(title="{}'s info".format(user.name), description="Here's what I could find.", color=0x3498DB)
    embed.add_field(name="Name", value=user.name, inline=True)
    embed.add_field(name="ID", value=user.id, inline=True)
    embed.add_field(name="Status", value=user.status, inline=True)
    embed.add_field(name="Highest role", value=user.top_role)
    embed.add_field(name="Joined", value=user.joined_at)
    embed.set_thumbnail(url=user.avatar_url)
    await bot.say(embed=embed)


@bot.command(pass_context=True)
async def serverinfo(ctx):
    embed = discord.Embed(name="{}'s info".format(ctx.message.server.name), description="Here's what I could find.", color=0x3498DB)
    embed.add_field(name="Name", value=ctx.message.server.name, inline=True)
    embed.add_field(name="ID", value=ctx.message.server.id, inline=True)
    embed.add_field(name="Roles", value="{}".format(len(ctx.message.server.roles)), inline=True)
    embed.add_field(name="Members", value="{}".format(len(ctx.message.server.members)))
    embed.set_thumbnail(url=ctx.message.server.icon_url)
    await bot.say(embed=embed)


@bot.command(pass_context=True)
async def help():
    em = discord.Embed(title="Commands:", description="A bot to make a dud feel cosy.", color=0x3498DB)
    em.add_field(name="--------------------------------------------------------------------------------", value="\u200b", inline=True)
    em.add_field(name="dud", value="Check if the bot is operational.", inline=True)
    em.add_field(name="add", value="Adds two numbers together. Usage: ]add 5 7", inline=True)
    em.add_field(name="roll", value="Rolls die. Usage: ]roll (number of die)d(number of sides)", inline=True)
    em.add_field(name="choose", value="Choose between options. Usage: ]choose cat dog", inline=True)
    em.add_field(name="play", value="Plays an audio file from the internet. Usage: ]play (video url)", inline=True)
    em.add_field(name="summon", value="Bot joins the voice channel the user is in.", inline=True)
    em.add_field(name="join", value="Bot joins the specified voice channel. Usage: ]join (channel name)", inline=True)
    em.add_field(name="stop", value="Stops playing audio and leaves the voice channel. Deletes the queue.", inline=True)
    em.add_field(name="volume", value="Changes audio volume. Usage: ]volume (number)", inline=True)
    em.add_field(name="pause", value="Pauses the audio file.", inline=True)
    em.add_field(name="resume", value="Resumes playing the audio file.", inline=False)
    em.add_field(name="skip", value="Skips the audio file and plays the next one in the queue.", inline=True)
    em.add_field(name="playing", value="Displays currently playing audio.", inline=True)
    em.add_field(name="info", value="Gives information about the user.", inline=False)
    em.add_field(name="serverinfo", value="Gives information about the server.", inline=False)
    em.set_thumbnail(url=bot.user.avatar_url)
    await bot.say(embed=em)


@bot.command(pass_context=True)
async def checkopus():
    if discord.opus.is_loaded():
        await bot.say("Opus shared library is lock & loaded.")


@bot.command(pass_context=True)
async def niceu():
    em = discord.Embed(title='VERY NICEU CAESAR-KUN', description='\u200b', colour=0xDEADBF)
    em.set_image(url="https://i.ytimg.com/vi/ffQmb-cNFuk/maxresdefault.jpg")
    await bot.say(embed=em)


bot.run(bot_token_file.read())
