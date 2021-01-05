import discord
from discord.ext import commands
from discord.utils import get
import youtube_dl
import os
import shutil
from os import system
import random 

TOKEN = 'Nzc2NTQ2NzAzOTA5ODQ3MDkz.X62deQ.raUbjjLDP0NNoVNJjOtLCF1jrdU'
BOT_PREFIX = '@'

bot = commands.Bot(command_prefix=BOT_PREFIX)
bot.remove_command('help')

@bot.event
async def on_ready():
    print("Logged in as: " + bot.user.name + "\n")

@bot.command()
async def help(ctx):
   channel = ctx.message.channel
   embed = discord.Embed(
       title = 'Help',
       description = 'Manual page for Rush',
       colour = discord.Colour.orange()
   )
   embed.set_author(name='Rush', icon_url = 'https://cdn.discordapp.com/app-icons/776546703909847093/85c2dd38dfb53f9ad3476415856872e6.png?size=64')
   embed.set_image(url='https://cdn.discordapp.com/app-icons/776546703909847093/85c2dd38dfb53f9ad3476415856872e6.png?size=64')
   embed.set_thumbnail(url='https://cdn.discordapp.com/app-icons/776546703909847093/85c2dd38dfb53f9ad3476415856872e6.png?size=64')
   embed.add_field(name = "@ping", value = 'Returns the latency.', inline = False)
   embed.add_field(name ="@erase", value = 'deletes messages in discord channel, if no value is set default value will be 0.', inline = True)
   embed.add_field(name = "@ask", value = 'Ask a question on the future and Rush will provide you with the answers.', inline = True)
   embed.add_field(name = "@play", value = 'Type the name of the song you wish to play from Youtube.', inline = True)
   embed.add_field(name = "@pause", value = 'Pause the current song.', inline = True)
   embed.add_field(name = "@resume", value = 'Resume playing the current song.', inline = True)
   embed.add_field(name = "@stop", value = 'This will stop playing the current song and clear it from the song queue.', inline = True)
   embed.add_field(name = "@queue", value = 'Places a song in queue along with any other songs in queue.', inline = True)
   embed.add_field(name = "@next", value = 'Skips to the next song.', inline = True)
   await ctx.send(embed = embed)



@bot.command()
async def ping(ctx):
    await ctx.send(f'Ahh here is the ping! {round(bot.latency *1000)}ms')


@bot.command(aliases = ['question','Ask','Question'])
async def ask(ctx, *, question):
    responses = ['I believe so.',
                 'Thats kind of a hard question, you do know I dont know everything right?',
                 'Your fate has already been decided, and it doesnt look to well :(',
                 'Yes you will be fine', 'I dont think that is a good idea', 'Doutbful',
                 'I dont know about that!', 'Most certainly!', 'Most Likely', '50/50 Chance',
                 'I would not count on it.','If you think its good then go for it', 'You should ask again, cause I dont think you will like the outcome.',
                 'You will do great!.','Cant preditct it right now', 'Again 50/50',
                 'I dont trust it.', 'Keep going and it will work out for you.','Yes.','No.']
    await ctx.send(f'Q: {question}\nA: {random.choice(responses)}') 

@ask.error
async def ask_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please input a question into the web of fates!')

@bot.command(aliases = ['purge','Erase','destroy','delete'])
@commands.has_permissions(manage_messages=True)
async def erase(ctx, amount = 1):
    await ctx.channel.purge(limit=amount+1)

@bot.command(pass_context=True, aliases=['Join', 'joi'])
async def join(ctx):
    global voice
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice is not None:
        return await voice.move_to(channel)
    
    await channel.connect()

    await ctx.send(f"Joined {channel}")


@bot.command(pass_context=True, aliases=['Leave','Disconnect','lea'])
async def leave(ctx):
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        await voice.disconnect()
        print(f"Rush has left {channel}")
        await ctx.send(f"Left {channel}")
    else:
        print("Rush was told to leave voice channel, but was not in one")
        await ctx.send("Don't think I am in a voice channel")




@bot.command(pass_context=True, aliases=['Play', 'pla'])
async def play(ctx, *url: str):

    def check_queue():
        Queue_infile = os.path.isdir("./Queue")
        if Queue_infile is True:
            DIR = os.path.abspath(os.path.realpath("Queue"))
            length = len(os.listdir(DIR))
            still_q = length - 1
            try:
                first_file = os.listdir(DIR)[0]
            except:
                print("No more queued song(s)\n")
                queues.clear()
                return
            main_location = os.path.dirname(os.path.realpath(__file__))
            song_path = os.path.abspath(os.path.realpath("Queue") + "\\" + first_file)
            if length != 0:
                print("Song done, playing next queued\n")
                print(f"Songs still in queue: {still_q}")
                song_there = os.path.isfile("song.mp3")
                if song_there:
                    os.remove("song.mp3")
                shutil.move(song_path, main_location)
                for file in os.listdir("./"):
                    if file.endswith(".mp3"):
                        os.rename(file, 'song.mp3')

                voice.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e: check_queue())
                voice.source = discord.PCMVolumeTransformer(voice.source)
                voice.source.volume = 0.07

            else:
                queues.clear()
                return

        else:
            queues.clear()
            print("No songs were queued before the ending of the last song\n")



    song_there = os.path.isfile("song.mp3")
    try:
        if song_there:
            os.remove("song.mp3")
            queues.clear()
            print("Removed old song file")
    except PermissionError:
        print("Trying to delete song file, but it's being played")
        await ctx.send("ERROR: Music playing")
        return


    Queue_infile = os.path.isdir("./Queue")
    try:
        Queue_folder = "./Queue"
        if Queue_infile is True:
            print("Removed old Queue Folder")
            shutil.rmtree(Queue_folder)
    except:
        print("No old Queue folder")

    await ctx.send("Setting up the audio track...")

    voice = get(bot.voice_clients, guild=ctx.guild)

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': False,
        'outtmpl': "./song.mp3",
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    song_search = " ".join(url)


    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        print("Downloading audio now\n")
        ydl.download([f"ytsearch1:{song_search}"])
    
    voice.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e: check_queue())
    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.volume = 0.07


@bot.command(pass_context=True, aliases=['pa', 'pau'])
async def pause(ctx):

    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_playing():
        print("Music paused")
        voice.pause()
        await ctx.send("Music paused")
    else:
        print("Music not playing failed pause")
        await ctx.send("Music not playing failed pause")


@bot.command(pass_context=True, aliases=['r', 'res'])
async def resume(ctx):

    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_paused():
        print("Resumed music")
        voice.resume()
        await ctx.send("Resumed music")
    else:
        print("Music is not paused")
        await ctx.send("Music is not paused")


@bot.command(pass_context=True, aliases=['s', 'sto'])
async def stop(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)

    queues.clear()

    queue_infile = os.path.isdir("./Queue")
    if queue_infile is True:
        shutil.rmtree("./Queue")

    if voice and voice.is_playing():
        print("Music stopped")
        voice.stop()
        await ctx.send("Music stopped")
    else:
        print("No music playing failed to stop")
        await ctx.send("No music playing failed to stop")


queues = {}

@bot.command(pass_context=True, aliases=['Queue', 'que'])
async def queue(ctx, *url: str):
    Queue_infile = os.path.isdir("./Queue")
    if Queue_infile is False:
        os.mkdir("Queue")
    DIR = os.path.abspath(os.path.realpath("Queue"))
    q_num = len(os.listdir(DIR))
    q_num += 1
    add_queue = True
    while add_queue:
        if q_num in queues:
            q_num += 1
        else:
            add_queue = False
            queues[q_num] = q_num

    queue_path = os.path.abspath(os.path.realpath("Queue") + f"\song{q_num}.%(ext)s")

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'outtmpl': queue_path,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    song_search = " ".join(url)

    
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        print("Downloading audio now\n")
        ydl.download([f"ytsearch1:{song_search}"])
   

    await ctx.send("Adding song " + str(q_num) + " to the queue")

    print("Song added to queue\n")


@bot.command(pass_context=True, aliases=['skip', 'nex'])
async def next(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_playing():
        print("Playing Next Song")
        voice.stop()
        await ctx.send("Next Song")
    else:
        print("No music playing")
        await ctx.send("No music playing failed")




bot.run(TOKEN)