"""https://github.com/lw/BluRay/wiki/PlayItem"""

__all__ = ['PlayItem',
           'STREAM_CODING_TYPE', 'VIDEO_FORMAT', 'FRAMERATE', 'DYNAMIC_RANGE_TYPE',
           'COLOR_SPACE', 'AUDIO_FORMAT', 'SAMPLE_RATE', 'CHARACTER_CODE']

from fractions import Fraction
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

            if self.stream_type == 0x01:
                ref, = self._unpack_byte(2)                                     # 2 bytes - 16 bits
                self.ref_to_stream_pid = '0x{:<04x}'.format(ref)

            elif self.stream_type == 0x02:
                self.ref_to_sub_path_id, = self._unpack_byte(1)                 # 1 byte - 8 bits
                self.ref_to_sub_clip_id, = self._unpack_byte(1)                 # 1 byte - 8 bits
                ref, = self._unpack_byte(2)                                     # 2 bytes - 16 bits
                self.ref_to_stream_pid = '0x{:<04x}'.format(ref)

            elif self.stream_type in {0x03, 0x04}:
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

    video_format: Optional[int]
    framerate: Optional[int]

    dynamic_range_type: Optional[int]
    colorspace: Optional[int]

    cr_flag_and_hdr_plus_flag = Optional[int]

    audio_format: Optional[int]
    samplerate: Optional[int]

    language_code: Union[str, bytes, None]
    character_code: Optional[int]

    def load(self):
        pos = self._get_pos()

        self.length, = self._unpack_byte(1)                                     # 1 byte - 8 bits

        if self.length != 0:
            self.stream_coding_type, = self._unpack_byte(1)                     # 1 byte - 8 bits

            if self.stream_coding_type in {0x01, 0x02, 0x1B, 0xEA}:
                # byte = "{0:08b}".format(self.mpls.read(1)[0])
                # self.video_format = byte[:4], 2)
                # self.framerate = byte[4:], 2)
                video_format_and_framerate, = self._unpack_byte(1)              # 1 byte - 8 bits
                self.video_format = video_format_and_framerate >> 4
                self.framerate = video_format_and_framerate - (self.video_format << 4)

            elif self.stream_coding_type == 0x24:
                video_format_and_framerate, = self._unpack_byte(1)              # 1 byte - 8 bits
                self.video_format = video_format_and_framerate >> 4
                self.framerate = video_format_and_framerate - (self.video_format << 4)

                dynamic_range_type_and_colorspace, = self._unpack_byte(1)       # 1 byte - 8 bits
                self.dynamic_range_type = dynamic_range_type_and_colorspace >> 4
                self.colorspace = dynamic_range_type_and_colorspace - (self.dynamic_range_type << 4)

                self.cr_flag_and_hdr_plus_flag, = self._unpack_byte(1)           # 1 byte - 8 bits

            elif self.stream_coding_type in {0x03, 0x04, 0x80, 0x81,
                                             0x82, 0x83, 0x84, 0x85,
                                             0x86, 0xA1, 0xA2}:
                audio_format_and_samplerate, = self._unpack_byte(1)             # 1 byte - 8 bits
                self.audio_format = audio_format_and_samplerate >> 4
                self.samplerate = audio_format_and_samplerate - (self.audio_format << 4)

                self.language_code = self.mpls.read(3).decode('utf-8')          # 3 bytes - 24 bits

            elif self.stream_coding_type in {0x90, 0x91}:
                self.language_code = self.mpls.read(3).decode('utf-8')          # 3 bytes - 24 bits

            elif self.stream_coding_type == 0x92:
                self.character_code, = self._unpack_byte(1)                     # 1 byte - 8 bits

                if self.character_code in CHARACTER_CODE:
                    encoding = CHARACTER_CODE[self.character_code]
                    self.language_code = self.mpls.read(3).decode(encoding)     # 3 bytes - 24 bits
                else:
                    print('WARNING: character_code was not a recognised value', self.character_code)
                    self.language_code = self.mpls.read(3)                      # 3 bytes - 24 bits

        self.mpls.seek(pos + self.length + 1)

        return self



STREAM_CODING_TYPE: Dict[int, str] = {
    0x01: 'MPEG-1 video stream',
    0x02: 'MPEG-2 video stream',
    0x1B: 'MPEG-4 AVC video stream',
    0x20: 'MPEG-4 MVC video stream',
    0xEA: 'SMTPE VC-1 video stream',
    0x24: 'HEVC video stream (including DV stream)',
    0x03: 'MPEG-1 audio stream',
    0x04: 'MPEG-2 audio stream',
    0x80: 'LPCM audio stream (primary audio)',
    0x81: 'Dolby Digital audio stream (primary audio)',
    0x82: 'DTS audio stream (primary audio)',
    0x83: 'Dolby Digital TrueHD audio stream (primary audio)',
    0x84: 'Dolby Digital Plus audio stream (primary audio)',
    0x85: 'DTS-HD High Resolution Audio audio stream (primary audio)',
    0x86: 'DTS-HD Master Audio audio stream (primary audio)',
    0xA1: 'Dolby Digital Plus audio stream (secondary audio)',
    0xA2: 'DTS-HD audio stream (secondary audio)',
    0x90: 'Presentation Graphics stream',
    0x91: 'Interactive Graphics stream',
    0x92: 'Text Subtitle stream'
}

VIDEO_FORMAT: Dict[int, str] = {
    1: '480pi',
    2: '576i',
    3: '480p',
    4: '1080i',
    5: '720p',
    6: '1080p',
    7: '576p',
    8: '2160p'
}

FRAMERATE: Dict[int, Fraction] = {
    1: Fraction(24000, 1001),
    2: Fraction(24),
    3: Fraction(25),
    4: Fraction(30000, 1001),
    6: Fraction(50),
    7: Fraction(60000, 1001)
}

DYNAMIC_RANGE_TYPE: Dict[int, str] = {
    0: 'SDR',
    1: 'HDR10',
    2: 'Dolby Vision'
}

COLOR_SPACE: Dict[int, str] = {
    0: 'Reserved',
    1: 'ITU-R Recommendation BT.709',
    2: 'ITU-R Recommendation BT.2020'
}

AUDIO_FORMAT: Dict[int, str] = {
    0x01: 'mono',
    0x03: 'stereo',
    0x06: 'multichannel',
    0x0C: 'stereo and multichannel',
}

SAMPLE_RATE: Dict[int, str] = {
    0x01: '48 KHz',
    0x04: '96 KHz',
    0x05: '192 KHz',
    0x0C: '48 & 192 KHz',
    0x0E: '48 & 96 KHz',
}

CHARACTER_CODE: Dict[int, str] = {
    0x01: 'utf-8',
    0x02: 'utf_16_be',
    0x03: 'shift_jis',
    0x04: 'euc_kr',
    0x05: 'gb18030',
    0x06: 'gb2312',
    0x07: 'big5',
}



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
            if self.still_mode == 0x01:
                self.still_time, = self._unpack_byte(2)                         # 2 bytes - 16 bits
            else:
                self.mpls.read(2)                                               # 2 bytes - 16 bits - Reserved

            if self.is_multi_angle:
                self.nb_angles, = self._unpack_byte(1)                          # 1 byte - 8 bits
                self.misc_flags_3, = self._unpack_byte(1)                       # 1 byte - 8 bits
                self.angles = []

                for _ in range(self.nb_angles):
                    clip_info = self.mpls.read(5).decode('utf-8')               # 5 bytes - 40 bits
                    clip_codec = self.mpls.read(4).decode('utf-8')              # 4 bytes - 32 bits
                    ref, = self._unpack_byte(1)                                 # 1 byte - 8 bits
                    self.angles.append(Angle(clip_info, clip_codec, ref))

            self.stn_table = STNTable(self.mpls).load()

        self.mpls.seek(pos + self.length + 2)

        return self
