"""https://github.com/lw/BluRay/wiki/PlayItem"""

__all__ = ['PlayItem']


from typing import Dict, List, NamedTuple, Optional, Tuple, Union

from .movie_playlist import MplsObject


class StreamEntry(MplsObject):
    """https://github.com/lerks/BluRay/wiki/StreamEntry"""
    length: int
    stream_type: Optional[int]
    ref_to_stream_pid: Optional[str]
    ref_to_sub_path_id: Optional[int]
    ref_to_sub_clip_id: Optional[int]

    def load(self):
        pos = self._get_pos()

        self.length, = self._unpack_byte(1)                                     # 1 byte - 8 bits

        if self.length != 0:
            self.stream_type, = self._unpack_byte(1)                            # 1 byte - 8 bits

            if self.stream_type == int(0x01):
                ref, = self._unpack_byte(2)                                     # 2 bytes - 16 bits
                self.ref_to_stream_pid = '0x{:<04x}'.format(ref)

            elif self.stream_type == int(0x02):
                self.ref_to_sub_path_id, = self._unpack_byte(1)                 # 1 byte - 8 bits
                self.ref_to_sub_clip_id, = self._unpack_byte(1)                 # 1 byte - 8 bits
                ref, = self._unpack_byte(2)                                     # 2 bytes - 16 bits
                self.ref_to_stream_pid = '0x{:<04x}'.format(ref)

            elif self.stream_type in {int(0x03), int(0x04)}:
                self.ref_to_sub_path_id, = self._unpack_byte(1)                 # 1 byte - 8 bits
                ref, = self._unpack_byte(2)                                     # 2 bytes - 16 bits
                self.ref_to_stream_pid = '0x{:<04x}'.format(ref)

            else:
                print('WARNING: stream_type was not a recognised value', self.stream_type)


        self.mpls.seek(pos + self.length + 1)

        return self


class StreamAttributes(MplsObject):
    """https://github.com/lw/BluRay/wiki/StreamAttributes"""
    length: int
    stream_coding_type: Optional[int]
    video_format_and_framerate: Optional[int]
    dynamic_range_type_and_colorspace: Optional[int]
    misc_flags_1: Optional[int]
    audio_format_and_samplerate: Optional[int]
    language_code: Union[str, bytes, None]
    character_code: Optional[int]

    def load(self):
        pos = self._get_pos()

        self.length, = self._unpack_byte(1)                                     # 1 byte - 8 bits

        if self.length != 0:
            self.stream_coding_type, = self._unpack_byte(1)                     # 1 byte - 8 bits

            if self.stream_coding_type in {int(0x01), int(0x02), int(0x1B), int(0xEA)}:
                self.video_format_and_framerate, = self._unpack_byte(1)         # 1 byte - 8 bits

            elif self.stream_coding_type == int(0x24):
                self.video_format_and_framerate, = self._unpack_byte(1)         # 1 byte - 8 bits
                self.dynamic_range_type_and_colorspace, = self._unpack_byte(1)  # 1 byte - 8 bits
                self.misc_flags_1, = self._unpack_byte(1)                       # 1 byte - 8 bits

            elif self.stream_coding_type in {int(0x03), int(0x04), int(0x80), int(0x81),
                                             int(0x82), int(0x83), int(0x84), int(0x85),
                                             int(0x86), int(0xA1), int(0xA2)}:
                self.audio_format_and_samplerate, = self._unpack_byte(1)        # 1 byte - 8 bits
                self.language_code = self.mpls.read(3).decode('utf-8')          # 3 bytes - 24 bits

            elif self.stream_coding_type in {int(0x90), int(0x91)}:
                self.language_code = self.mpls.read(3).decode('utf-8')          # 3 bytes - 24 bits

            elif self.stream_coding_type == int(0x92):
                self.character_code, = self._unpack_byte(1)                     # 1 byte - 8 bits

                if self.character_code in self._char_code_enc:
                    encoding = self._get_char_code_enc(self.character_code)
                    self.language_code = self.mpls.read(3).decode(encoding)     # 3 bytes - 24 bits
                else:
                    print('WARNING: character_code was not a recognised value', self.character_code)
                    self.language_code = self.mpls.read(3)                      # 3 bytes - 24 bits

        self.mpls.seek(pos + self.length + 1)

        return self

    def _get_char_code_enc(self, char_code: int) -> str:
        return self._char_code_enc()[char_code]

    @staticmethod
    def _char_code_enc() -> Dict[int, str]:
        char_code_enc: Dict[int, str] = {
            int(0x01): 'utf-8',
            int(0x02): 'utf_16_be',
            int(0x03): 'shift_jis',
            int(0x04): 'euc_kr',
            int(0x05): 'gb18030',
            int(0x06): 'gb2312',
            int(0x07): 'big5',
        }
        return char_code_enc



EntryStreams = List[Tuple[StreamEntry, StreamAttributes]]


class STNTable(MplsObject):
    """https://github.com/lw/BluRay/wiki/STNTable"""
    length: int
    nb_prim_video_stream_entries: Optional[int]
    nb_prim_audio_stream_entries: Optional[int]
    nb_prim_pgs_stream_entries: Optional[int]
    nb_prim_igs_stream_entries: Optional[int]
    nb_seco_audio_stream_entries: Optional[int]
    nb_seco_video_stream_entries: Optional[int]
    nb_seco_pgs_stream_entries: Optional[int]
    nb_dv_stream_entries: Optional[int]
    prim_video_stream_entries: Optional[EntryStreams]
    prim_audio_stream_entries: Optional[EntryStreams]
    prim_pgs_stream_entries: Optional[EntryStreams]
    seco_pgs_stream_entries: Optional[EntryStreams]
    prim_igs_stream_entries: Optional[EntryStreams]
    seco_audio_stream_entries: Optional[EntryStreams]
    seco_video_stream_entries: Optional[EntryStreams]
    dv_stream_entries: Optional[EntryStreams]

    stream_entries: Tuple

    def load(self):
        pos = self._get_pos()

        self.length, = self._unpack_byte(2)                                     # 2 bytes - 16 bits

        if self.length != 0:
            self.mpls.read(2)                                                   # 2 bytes - 16 bits - Reserved
            self.nb_prim_video_stream_entries, = self._unpack_byte(1)           # 1 byte - 8 bits
            self.nb_prim_audio_stream_entries, = self._unpack_byte(1)           # 1 byte - 8 bits
            self.nb_prim_pgs_stream_entries, = self._unpack_byte(1)             # 1 byte - 8 bits
            self.nb_prim_igs_stream_entries, = self._unpack_byte(1)             # 1 byte - 8 bits
            self.nb_seco_audio_stream_entries, = self._unpack_byte(1)           # 1 byte - 8 bits
            self.nb_seco_video_stream_entries, = self._unpack_byte(1)           # 1 byte - 8 bits
            self.nb_seco_pgs_stream_entries, = self._unpack_byte(1)             # 1 byte - 8 bits
            self.nb_dv_stream_entries, = self._unpack_byte(1)                   # 1 byte - 8 bits
            self.mpls.read(4)                                                   # 4 bytes - 32 bits - Reserved


            nbs = (
                self.nb_prim_video_stream_entries, self.nb_prim_audio_stream_entries,
                self.nb_prim_pgs_stream_entries, self.nb_seco_pgs_stream_entries,
                self.nb_prim_igs_stream_entries, self.nb_seco_audio_stream_entries,
                self.nb_seco_video_stream_entries, self.nb_dv_stream_entries
            )

            __stream_entries: List[EntryStreams] = []

            for nb in nbs:
                entry_streams: EntryStreams = []
                for _ in range(nb):
                    stream_entry = StreamEntry(self.mpls).load()
                    stream_attributes = StreamAttributes(self.mpls).load()
                    entry_streams.append((stream_entry, stream_attributes))
                __stream_entries.append(entry_streams)

            self.prim_video_stream_entries, self.prim_audio_stream_entries, \
                self.prim_pgs_stream_entries, self.seco_pgs_stream_entries, \
                self.prim_igs_stream_entries, self.seco_audio_stream_entries, \
                self.seco_video_stream_entries, self.dv_stream_entries = __stream_entries


        self.mpls.seek(pos + self.length + 2)

        return self


class Angle(NamedTuple):
    """https://github.com/lw/BluRay/wiki/PlayItem"""
    clip_information_filename: str
    clip_codec_identifier: str
    ref_to_stcid: int


class PlayItem(MplsObject):
    """https://github.com/lw/BluRay/wiki/PlayItem"""
    length: int
    clip_information_filename: Optional[str]
    clip_codec_identifier: Optional[str]
    misc_flags_1: Optional[int]
    is_multi_angle: Optional[bool]
    ref_to_stcid: Optional[int]
    intime: Optional[int]
    outtime: Optional[int]
    uo_mask_table: Optional[int]
    misc_flags_2: Optional[int]
    still_mode: Optional[int]
    still_time: Optional[int]
    nb_angles: Optional[int]
    misc_flags_3: Optional[int]
    angles: Optional[List[Angle]]
    stn_table: Optional[STNTable]

    def load(self):
        pos = self._get_pos()

        self.length, = self._unpack_byte(2)

        if self.length != 0:
            self.clip_information_filename = self.mpls.read(5).decode('utf-8')  # 5 bytes - 40 bits
            self.clip_codec_identifier = self.mpls.read(4).decode('utf-8')      # 4 bytes - 32 bits

            self.misc_flags_1, = self._unpack_byte(2)                           # 2 bytes - 16 bits - Reserved
            self.is_multi_angle = bool(self.misc_flags_1 & (1 << 16 - 1 - 11))  # Condition

            self.ref_to_stcid, = self._unpack_byte(1)                           # 1 byte - 8 bits
            self.intime, = self._unpack_byte(4)                                 # 4 bytes - 32 bits
            self.outtime, = self._unpack_byte(4)                                # 4 bytes - 32 bits
            self.uo_mask_table, = self._unpack_byte(8)                          # 8 bytes - 64 bits
            self.misc_flags_2, = self._unpack_byte(1)                           # 1 byte - 8 bits

            self.still_mode, = self._unpack_byte(1)                             # 1 byte - 8 bits
            if self.still_mode == int(0x01):
                self.still_time, = self._unpack_byte(2)                         # 2 bytes - 16 bits
            else:
                self.mpls.read(2)                                               # 2 bytes - 16 bits - Reserved

            if self.is_multi_angle:
                self.nb_angles, = self._unpack_byte(1)                          # 1 byte - 8 bits
                self.misc_flags_3, = self._unpack_byte(1)                       # 1 byte - 8 bits

                for _ in range(self.nb_angles):
                    clip_info = self.mpls.read(5).decode('utf-8')               # 5 bytes - 40 bits
                    clip_codec = self.mpls.read(4).decode('utf-8')              # 4 bytes - 32 bits
                    ref, = self._unpack_byte(1)                                 # 1 byte - 8 bits
                    self.angles.append(Angle(clip_info, clip_codec, ref))

            self.stn_table = STNTable(self.mpls).load()

        self.mpls.seek(pos + self.length + 2)

        return self
