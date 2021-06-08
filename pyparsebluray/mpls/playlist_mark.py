"""https://github.com/lw/BluRay/wiki/PlayListMark"""
from typing import List, NamedTuple, Optional

from .movie_playlist import MplsObject


class PlaylistMark(NamedTuple):
    """https://github.com/lw/BluRay/wiki/PlayListMark"""
    mark_type: int
    ref_to_play_item_id: int
    mark_timestamp: int
    entry_espid: int
    duration: int


class PlaylistMarks(MplsObject):
    """https://github.com/lw/BluRay/wiki/PlayListMark"""
    length: int
    nb_playlist_marks: Optional[int]
    playlist_marks: Optional[List[PlaylistMark]]

    def load(self):
        pos = self._get_pos()

        self.length, = self._unpack_byte(4)                                     # 4 bytes - 32 bits

        if self.length != 0:
            self.nb_playlist_marks, = self._unpack_byte(2)                      # 2 bytes - 16 bits

            if self.nb_playlist_marks > 0:
                for _ in range(self.nb_playlist_marks):
                    self.mpls.read(1)                                           # 1 byte - 8 bits - Reserved
                    mark_type, = self._unpack_byte(1)                           # 1 byte - 8 bits
                    ref_to_play_item_id, = self._unpack_byte(2)                 # 2 bytes - 16 bits
                    mark_timestamp, = self._unpack_byte(4)                      # 4 bytes - 32 bits
                    entry_espid, = self._unpack_byte(2)                         # 2 bytes - 16 bits
                    duration, = self._unpack_byte(4)                            # 4 bytes - 32 bits

                    self.playlist_marks.append(
                        PlaylistMark(mark_type, ref_to_play_item_id,
                                     mark_timestamp, entry_espid, duration)
                    )

        self.mpls.seek(pos + self.length + 4)

        return self
