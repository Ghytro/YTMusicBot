from discord import channel
from storage_manager import StorageManager
from playlist import Playlist
import discord
from config import settings
from helpers import *
import os


class YtMusicBot(discord.Client):
    storage_manager = StorageManager()
    playlists = {} # key: text channel id, value: playlist object


    async def invoke_callback(self, msg, command, args = []):
        await getattr(self, command)(msg, args)


    async def setup(self, msg, args):
        # check if there's a channel for the bot requests
        guild = msg.channel.guild
        if settings["request_channel"] not in [str(x) for x in guild.text_channels]:
            channel = await guild.create_text_channel(settings["request_channel"])
            self.playlists[channel.id] = Playlist()
            dump_channel_to_backup(channel.id)


    async def play(self, msg, args):
        playlist = self.playlists[msg.channel.id]
        if playlist.voice_client.is_playing():
            await msg.channel.send("I'm already playing")
            return
        if len(playlist.queue) == 0:
            await msg.channel.send("Playlist is empty, nothing to play")
            return
        # trying to connect to voice channel where we need
        if playlist.voice_client is None or not playlist.voice_client.is_connected():
            try:
                playlist.voice_client = await msg.author.voice.channel.connect()
            except:
                await msg.channel.send("Unable to connect to voice channel")
                return
        # checking if we're paused
        if playlist.voice_client.is_paused():
            playlist.voice_client.resume()
            playlist.is_playing = True
            return
        # playing last song we were playing
        await start_playlist(msg, playlist)


    async def skip(self, msg, args):
        playlist = self.playlists[msg.channel.id]
        if playlist.voice_client is None or not playlist.voice_client.is_connected():
            return
        playlist.voice_client.stop()


    async def prev(self, msg, args):
        playlist = self.playlists[msg.channel.id]
        if playlist.voice_client is None or not playlist.voice_client.is_connected():
            return
        playlist.pos -= 2
        if playlist.pos == -2 and playlist.loop_playlist:
            playlist.pos = len(playlist.get_queue()) - 2
        playlist.voice_client.stop()


    async def queue(self, msg, args):
        reply = "```css\nCurrent queue:\n"
        playlist = self.playlists[msg.channel.id]
        for i, name in enumerate(playlist.queue):
            reply += f"{i + 1}. {name}" + ("< Now playing\n" if i == playlist.pos else "\n")
        reply += "```"
        await msg.channel.send(reply)


    async def pause(self, msg, args):
        playlist = self.playlists[msg.channel.id]
        if not playlist.voice_client.is_paused():
            playlist.voice_client.pause()


    async def stop(self, msg, args):
        playlist = self.playlists[msg.channel.id]
        if playlist.voice_client.is_playing():
            playlist.is_playing = False
            playlist.voice_client.stop()
            playlist.pos -= 1


    async def goto(self, msg, args):
        playlist = self.playlists[msg.channel.id]
        index = int(args[0])
        if index > len(playlist.queue) or index <= 0:
            await msg.channel.send("No such position in playlist")
            return
        playlist.pos = index - 2
        playlist.voice_client.stop()
        await start_playlist(msg, playlist)

    async def leave(self, msg, args):
        playlist = self.playlists[msg.channel.id]
        await playlist.voice_client.disconnect()
        playlist = Playlist()

    async def on_ready(self):
        print(f"Bot logged in as {self.user}")

        # load created channels from file
        if os.path.exists("backup_channels.txt"):
            with open("backup_channels.txt", "r") as backup_file:
                self.playlists = {int(x): Playlist() for x in backup_file.read().split()}
        print(self.playlists)


    async def on_message(self, msg):
        if msg.author == self.user: # idk why discord api doesnt handle this shit
            return
        if is_command(msg.content):
            await self.invoke_callback(msg, msg.content[len(settings["prefix"]):].split()[0], msg.content[len(settings["prefix"]):].split()[1:])
            return
        if msg.channel.id not in self.playlists.keys():
            return

        # the case when the message is in channel for bot
        if msg.content in settings["commands"]:
            command = transform_to_synonim(msg.content)
            await self.invoke_callback(msg, command)
            return

        if msg.content.split()[0] in settings['commands']:
            if msg.content.split()[0] == "goto":
                await self.invoke_callback(msg, msg.content.split()[0], [int(msg.content.split()[1])])
            return

        # the case when we need to add song to playlist
        apologies = await msg.channel.send("Downloading your song, this might take a while... (corpo faggots limiting download speed for api)")
        title, path = await self.storage_manager.download_song(msg.content)
        playlist = self.playlists[msg.channel.id]
        playlist.add_song(title, path)
        await apologies.delete()
        if playlist.voice_client is None or not playlist.voice_client.is_connected():
            try:
                playlist.voice_client = await msg.author.voice.channel.connect()
            except:
                await msg.channel.send("Unable to connect to voice channel")
                return
        if not playlist.voice_client.is_playing() and not playlist.voice_client.is_paused():
            await start_playlist(msg, playlist)
        else:
            await msg.channel.send(f"{title} is added to the queue")


def test_downloader():
    queries = ["vaxei firelight", "the words i never said nightcore"]
    downloader = StorageManager()
    for i, q in enumerate(queries):
        title, filename = downloader.download_song(q)
        print(f"{i + 1}) Title: {title}, filename: {filename}")


bot = YtMusicBot()


def main():
    bot.run(settings['token'])

if __name__ == "__main__":
    main()
