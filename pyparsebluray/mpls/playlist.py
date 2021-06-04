"""https://github.com/lw/BluRay/wiki/PlayList"""

__all__ = ['Playlist']


from typing import List, Optional

from .movie_playlist import MplsObject
from .play_item import PlayItem
from .sub_path import SubPath


class Playlist(MplsObject):
    """https://github.com/lw/BluRay/wiki/PlayList"""
    length: int
    nb_play_items: Optional[int]
    nb_sub_paths: Optional[int]
    play_items: Optional[List[PlayItem]] = []
    sub_paths: Optional[List[SubPath]] = []

    def load(self):
        pos = self._get_pos()

        self.length, = self._unpack_byte(4)                                     # 4 bytes - 32 bits

        if self.length != 0:
            self.mpls.read(2)                                                   # 2 bytes - 16 bits
            self.nb_play_items, = self._unpack_byte(2)                          # 2 bytes - 16 bits
            self.nb_sub_paths, = self._unpack_byte(2)                           # 2 bytes - 16 bits

            self.play_items += [PlayItem(self.mpls).load() for _ in range(self.nb_play_items)]
            self.sub_paths += [SubPath(self.mpls).load() for _ in range(self.nb_sub_paths)]

        self.mpls.seek(pos + self.length + 4)

        return self
