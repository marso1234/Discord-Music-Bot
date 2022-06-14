import discord
from discord.ext import commands
from youtube_dl import YoutubeDL
import yt_dlp
import asyncio

FFMPEG_OPTIONS = {
    'before_options':
    '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}
YDL_OPTIONS = {'format': 'bestaudio/best'}
loop = asyncio.get_event_loop()
asyncio.set_event_loop(loop)


class music(commands.Cog):
    song_queue = []  #Contains  Url
    title = []  #Contains Title
    now_playing = ''

    def __init(self, client):
        self.client = client

    async def async_next(self, ctx):
        await ctx.send(f"`Playing {self.now_playing} {len(self.title)} left`")

    async def async_end(self, ctx):
        await ctx.send(f"`No more song in queue`")

    def play_next(self, ctx):
        print("Try Next...")
        if len(self.song_queue) >= 1:
            source = self.song_queue[0]
            self.now_playing = self.title[0]
            del self.song_queue[0]
            del self.title[0]
            vc = ctx.voice_client
            asyncio.run_coroutine_threadsafe(self.async_next(ctx), loop)
            vc.play(discord.FFmpegOpusAudio(source=source, **FFMPEG_OPTIONS),
                    after=lambda e: print('Player error: %s' % e)
                    if e else self.play_next(ctx))
        else:
            asyncio.run_coroutine_threadsafe(self.async_end(ctx), loop)

    @commands.command(brief='Clear queue')
    async def clear(self, ctx):
        self.song_queue = []
        self.title = []
        self.now_playing = ''
        await ctx.send('Queue Cleared')

    @commands.command(brief='View current queue')
    async def queue(self, ctx, max_amount=15):
        if self.now_playing != "":
            await ctx.send('Now Playing:')
            await ctx.send(self.now_playing)
        if len(self.title) >= 1:
            await ctx.send('\nCurrent Queue:')
            await ctx.send('\n'.join(self.title[0:max_amount]))
            if len(self.title) - max_amount > 0:
                await ctx.send('And {Amount} More...'.format(
                    Amount=len(self.title) - max_amount))

    @commands.command(brief='Skip current song')
    async def skip(self, ctx):
        ctx.voice_client.pause()
        await ctx.send('Skipped')
        self.play_next(ctx)

    @commands.command(brief='Join chatroom')
    async def join(self, ctx):
        if ctx.author.voice is None:
            await ctx.send("You are not in voice channel")
        voice_channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await voice_channel.connect()
        else:
            await ctx.voice_client.move_to(voice_channel)
        return ctx

    @commands.command(brief='Disconnect from chatroom')
    async def disconnect(self, ctx):
        await self.clear(ctx)
        await ctx.voice_client.disconnect()
        await ctx.send('Disconnected')

    @commands.command(brief='<Youtube Link> Add music to queue')
    async def play(self, ctx, url):
        await ctx.send("Fetching...\nPlease Be Patient")

        with YoutubeDL(YDL_OPTIONS) as ydl:
            ydl._ies = [ydl.get_info_extractor('YoutubeTab'),ydl.get_info_extractor('Youtube')]
            info = ydl.extract_info(url, download=False)
            
            songs = []
            try:
                self.song_queue.append(info['formats'][0]['url'])
                self.title.append('>{title}'.format(title=info['title']))
            except:
                try:
                    songs = info['entries']
                    for song in songs:
                        self.song_queue.append(song['url'])
                        self.title.append(
                            '>{title}'.format(title=song.get('title')))
                except:
                    return
        if len(self.title) >= 100:
            return
        await self.queue(ctx, 15)
        ctx = await self.join(ctx)
        vc = ctx.voice_client
        if not vc.is_playing():
            self.play_next(ctx)
        else:
            await ctx.send('Song queued')

    @commands.command(brief='<Youtube Link> Looping a music/playlist')
    async def loop(self, ctx, url):
        ctx = await self.join(ctx)
        YDL_OPTIONS = {'format': 'bestaudio/best'}
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            await ctx.send("Fetching...")
            info = ydl.extract_info(url, download=False)
            songs = []
            await self.clear(ctx)
            try:
                self.song_queue.append(info['formats'][0]['url'])
                self.title.append('>{title}'.format(title=info['title']))
            except:
                try:
                    songs = info['entries']
                    for song in songs:
                        self.song_queue.append(song['url'])
                        self.title.append(
                            '>{title}'.format(title=song.get('title')))
                except:
                    return
            if len(self.title) != 0:
                while len(self.title) < 100:
                    for i in range(len(self.title)):
                        self.title.append(self.title[i])
                        self.song_queue.append(self.song_queue[i])
                        if len(self.title) == 100:
                            break
                self.skip(ctx)

    @commands.command(brief='Pause current music')
    async def pause(self, ctx):
        ctx.voice_client.pause()
        await ctx.send('Paused')

    @commands.command(brief='Resume current music')
    async def resume(self, ctx):
        ctx.voice_client.resume()
        await ctx.send('Resume')


def setup(client):
    client.add_cog(music(client))
