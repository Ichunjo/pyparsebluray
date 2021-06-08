"""https://github.com/lw/BluRay/wiki/ExtensionData"""

__all__ = ['ExtensionData']


from typing import List, NamedTuple, Optional

from .movie_playlist import MplsObject


class ExtensionDataEntry(NamedTuple):
    """https://github.com/lw/BluRay/wiki/ExtensionData"""
    ext_data_type: int
    ext_data_version: int
    ext_data_start_address: int
    ext_data_length: int


class ExtensionData(MplsObject):
    """https://github.com/lw/BluRay/wiki/ExtensionData"""
    length: int
    data_block_start_address: Optional[int]
    nb_ext_data_entries: Optional[int]
    ext_data_entries: Optional[List[ExtensionDataEntry]]

    def load(self):
        pos = self._get_pos()

        self.length, = self._unpack_byte(4)                                     # 4 bytes - 32 bits

        if self.length != 0:
            self.data_block_start_address, = self._unpack_byte(4)               # 4 bytes - 32 bits
            self.mpls.read(3)                                                   # 3 bytes - 24 bits - Reserved
            self.nb_ext_data_entries, = self._unpack_byte(1)                    # 1 byte - 8 bits

            self.ext_data_entries = []

            if self.nb_ext_data_entries > 0:
                for _ in range(self.nb_ext_data_entries):
                    ext_data_type, = self._unpack_byte(2)                       # 2 bytes - 16 bits
                    ext_data_version, = self._unpack_byte(2)                    # 2 bytes - 16 bits
                    ext_data_start_address, = self._unpack_byte(4)              # 4 bytes - 32 bits
                    ext_data_length, = self._unpack_byte(4)                     # 4 bytes - 32 bits

                    self.ext_data_entries.append(
                        ExtensionDataEntry(ext_data_type, ext_data_version,
                                           ext_data_start_address, ext_data_length)
                    )

        self.mpls.seek(pos + self.length + 4)

        return self
