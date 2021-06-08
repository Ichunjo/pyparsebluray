"""https://github.com/lw/BluRay/wiki/SubPath"""

__all__ = ['SubPath']


from typing import List, NamedTuple, Optional

from .movie_playlist import MplsObject


class MultiClipEntry(NamedTuple):
    """https://github.com/lw/BluRay/wiki/SubPlayItem"""
    clip_information_filename: str
    clip_codec_identifier: str
    ref_to_stcid: int


class SubPlayItem(MplsObject):
    """https://github.com/lw/BluRay/wiki/SubPlayItem"""
    length: int
    clip_information_filename: Optional[str]
    clip_codec_identifier: Optional[str]
    misc_flags_1: Optional[int]
    is_multi_clip_entries: Optional[bool]
    ref_to_stcid: Optional[int]
    intime: Optional[int]
    outtime: Optional[int]
    sync_play_item_id: Optional[int]
    sync_start_pts: Optional[int]
    nb_multi_clip_entries: Optional[int]
    multi_clip_entries: Optional[List[MultiClipEntry]]

    def load(self):
        pos = self._get_pos()

        self.length, = self._unpack_byte(2)                                     # 2 bytes - 16 bits

        if self.length != 0:
            self.clip_information_filename = self.mpls.read(5).decode('utf-8')  # 5 bytes - 40 bits
            self.clip_codec_identifier = self.mpls.read(4).decode('utf-8')      # 4 bytes - 32 bits
            self.misc_flags_1, = self._unpack_byte(4)                           # 4 bytes - 32 bits
            self.is_multi_clip_entries = bool(self.misc_flags_1 & (1 << 32 - 1 - 27))
            self.ref_to_stcid, = self._unpack_byte(1)                           # 1 byte - 8 bits
            self.intime, = self._unpack_byte(4)                                 # 4 bytes - 32 bits
            self.outtime, = self._unpack_byte(4)                                # 4 bytes - 32 bits
            self.sync_play_item_id, = self._unpack_byte(2)                      # 2 bytes - 16 bits
            self.sync_start_pts, = self._unpack_byte(4)                         # 4 bytes - 32 bits

            if self.is_multi_clip_entries:
                self.nb_multi_clip_entries, = self._unpack_byte(1)
                self.mpls.read(1)

                for _ in range(self.nb_multi_clip_entries):
                    clip_info = self.mpls.read(5).decode('utf-8')               # 5 bytes - 40 bits
                    clip_codec = self.mpls.read(4).decode('utf-8')              # 4 bytes - 32 bits
                    ref, = self._unpack_byte(1)                                 # 1 byte - 8 bits
                    self.multi_clip_entries.append(MultiClipEntry(clip_info, clip_codec, ref))

        self.mpls.seek(pos + self.length + 2)

        return self


class SubPath(MplsObject):
    """https://github.com/lw/BluRay/wiki/SubPath"""
    length: int
    sub_path_type: Optional[int]
    misc_flags_1: Optional[int]
    nb_sub_play_items: Optional[int]
    sub_play_items: Optional[List[SubPlayItem]]

    def load(self):
        pos = self._get_pos()

        self.length, = self._unpack_byte(4)                                     # 4 bytes - 32 bits

        if self.length != 0:
            self.mpls.read(1)
            self.sub_path_type, = self._unpack_byte(1)                          # 1 byte - 8 bits
            self.misc_flags_1, = self._unpack_byte(2)                           # 2 bytes - 16 bits
            self.mpls.read(1)
            self.nb_sub_play_items, = self._unpack_byte(1)                      # 1 byte - 8 bits

            self.sub_play_items = [SubPlayItem(self.mpls).load() for _ in range(self.nb_sub_play_items)]

        self.mpls.seek(pos + self.length + 4)

        return self
