from __future__ import unicode_literals
from youtube_dl import YoutubeDL
import urllib.request
import re
import os
from threading import Thread
from helpers import download_song_from_thread
import asyncio


class StorageManager:
    def __init__(self, storage_dir: str = "storage"):
        self.storage_dir = storage_dir
        self.downloaded_ids = set()
        if not os.path.exists(self.storage_dir):
            os.mkdir(self.storage_dir)
        
        # get all video ids that are already downloaded
        self.downloaded_ids = set([x.split('.')[0] for x in os.listdir(self.storage_dir) if os.path.isfile(os.path.join(self.storage_dir, x))])


    async def download_song(self, query: str):
        query = "+".join(query.split())
        html = urllib.request.urlopen(f"https://www.youtube.com/results?search_query={query}")
        video_id = re.findall(r"watch\?v=(\S{11})", html.read().decode())[0]
        video_url = f"https://www.youtube.com/watch?v={video_id}"

        ydl_opts = {
            'format': 'worstaudio',
            'outtmpl': f"{self.storage_dir}/{video_id}" + '.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        params = {"title": None}
        network_thread = Thread(target=download_song_from_thread, args=(ydl_opts, video_url, video_id, self.downloaded_ids, params))
        network_thread.start()
        while params["title"] is None:
            await asyncio.sleep(.5)
        network_thread.join()
        self.downloaded_ids.add(video_id)
        return (params["title"], f"{self.storage_dir}/{video_id}.mp3")
