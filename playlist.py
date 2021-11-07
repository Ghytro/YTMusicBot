import random
from dataclasses import dataclass

class Playlist:

    @dataclass(frozen=True)
    class Song:
        title: str
        path: str
        def __str__(self):
            return self.title


    queue: 'list[Song]' = []
    queue_shuffled: 'list[Song]' = []
    pos: int = -1
    loop_playlist: bool = True
    loop_current: bool = False
    shuffled: bool = False
    is_playing: bool = False
    voice_client = None


    def add_song(self, title: str, path: str) -> None:
        self.queue.append(Playlist.Song(title, path))
        self.queue_shuffled.append(Playlist.Song(title, path))


    def get_queue(self) -> 'list[Song]':
        """Get current queue according to shuffle"""
        return self.queue if not self.shuffled else self.queue_shuffled


    def current_song(self) -> Song:
        return self.get_queue()[self.pos]


    def switch_loop_playlist(self) -> bool:
        self.loop_playlist = not self.loop_playlist
        return self.loop_playlist


    def switch_loop_current(self):
        self.loop_current = not self.loop_current
        return self.loop_current


    def switch_shuffled(self) -> bool:
        """Shuffles playlist only after current pos"""
        if not self.shuffled:
            self.queue_shuffled = self.queue[:self.pos] + random.sample(self.queue[self.pos + 1:])
        self.shuffled = not self.shuffled
        return self.shuffled


    def next_song(self) -> Song:
        """Increments playlist iterator and returns song the iterator points"""
        if not self.loop_current:
            self.pos += 1
        if self.pos >= len(self.get_queue()) or self.pos < 0:
            if self.loop_playlist:
                self.pos = 0
            else:
                self.pos = -1
                raise IndexError("Attempt to move playlist iterator out of range")
        return self.current_song()


    def prev_song(self) -> Song:
        """Decrements playlist iterator and returns song the iterator points"""
        if not self.loop_current:
            self.pos -= 1
        if self.pos - 1 < 0 or self.pos >= len(self.get_queue()):
            if self.loop_playlist:
                self.pos = len(self.get_queue()) - 1
            else:
                self.pos = -1
                raise IndexError("Attempt to move playlist iterator out of range")
        return self.current_song()


    def custom_song(self, new_pos: int) -> Song:
        """Places playlist iterator in given position and returns song the iterator points
        Throws IndexError if the new pos is out of range"""
        if new_pos < 0 or new_pos >= len(self.get_queue()):
            raise IndexError("New playlist pos is out of range")
        self.pos = new_pos
        return self.current_song()
