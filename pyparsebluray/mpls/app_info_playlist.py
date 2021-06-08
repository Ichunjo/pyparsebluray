"""https://github.com/lw/BluRay/wiki/AppInfoPlayList"""

__all__ = ['AppInfoPlaylist']


from typing import Optional

from .movie_playlist import MplsObject


class AppInfoPlaylist(MplsObject):
    """https://github.com/lw/BluRay/wiki/AppInfoPlayList"""
    length: int
    playback_type: Optional[int]
    playback_count: Optional[int]
    uo_mask_table: Optional[int]
    misc_flags: Optional[int]

    def load(self):
        pos = self._get_pos()

        self.length, = self._unpack_byte(4)                                            # 4 bytes - 32 bits

        if self.length != 0:
            self.playback_type, = self._unpack_byte(1)                                 # 1 byte - 8 bits
            if self.playback_type in {0x02, 0x03}:
                self.playback_count, = self._unpack_byte(2)                            # 2 bytes - 16 bits
            else:
                self.mpls.read(2)                                                            # 2 bytes - 16 bits - Reserved
            self.uo_mask_table, = self._unpack_byte(8)                                 # 8 bytes - 64 bits
            self.misc_flags, = self._unpack_byte(2)                                    # 2 bytes - 16 bits

        self.mpls.seek(pos + self.length + 4)

        return self
