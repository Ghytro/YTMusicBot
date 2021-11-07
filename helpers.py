import asyncio
from config import settings
import os
import discord
from youtube_dl import YoutubeDL


def is_command(message_content: str) -> bool:
    return message_content.startswith(settings['prefix'])


def dump_channel_to_backup(channel_id: int) -> None:
    first = not os.path.exists("backup_channels.txt")
    with open("backup_channels.txt", "a") as backup_file:
        backup_file.write(f"{channel_id}" if first else f" {channel_id}")


def transform_to_synonim(command: str) -> str:
    synonims = {
        ("play", "p"): "play",
        ("skip", "next"): "skip",
        ("prev", "previous", "back"): "prev",
    }
    for k, v in synonims.items():
        if command in k:
            return v
    return command


async def start_playlist(msg, playlist):
    playlist.is_playing = True
    try:
        await msg.channel.send(f"Now playing: {playlist.next_song().title}")
    except IndexError:
        playlist.pos = -1
        playlist.is_playing = False
        return
    if playlist.voice_client.is_playing():
        playlist.voice_client.stop()
    playlist.voice_client.play(discord.FFmpegPCMAudio(
        source=playlist.current_song().path,
        executable="C:/ffmpeg/ffmpeg.exe"
        )
    )
    while playlist.voice_client.is_playing() or playlist.voice_client.is_paused():
        await asyncio.sleep(.5)
    if playlist.is_playing:
        await start_playlist(msg, playlist)


def download_song_from_thread(ydl_opts, video_url, video_id, downloaded_ids, params):
    with YoutubeDL(ydl_opts) as ydl:
        params['title'] = ydl.extract_info(video_url, download=video_id not in downloaded_ids).get('title', '')
