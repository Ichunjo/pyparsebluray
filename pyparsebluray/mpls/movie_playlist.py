"""https://github.com/lw/BluRay/wiki/MPLS"""

__all__ = ['MoviePlaylist']


from abc import ABC, abstractmethod
from io import BufferedReader
from struct import unpack
from typing import Any, Dict, Tuple


class MplsObject(ABC):
    """Abstract MPLS object interface"""
    mpls: BufferedReader

    def __init__(self, mpls: BufferedReader) -> None:
        self.mpls = mpls
        super().__init__()

    def __repr__(self) -> str:
        try:
            from prettyprinter import pretty_call, pretty_repr, register_pretty
            from prettyprinter.doc import Doc
            from prettyprinter.prettyprinter import PrettyContext

            @register_pretty(MplsObject)
            def _repr(value: object, ctx: PrettyContext) -> Doc:
                dic = vars(value)
                del dic['mpls']
                return pretty_call(ctx, MplsObject, dic)

            return pretty_repr(self)
        except ImportError:
            from pprint import pformat

            return pformat(vars(self), sort_dicts=False)

    @abstractmethod
    def load(self):
        """Method loading the MPLS object"""

    def _get_pos(self) -> int:
        return self.mpls.tell()

    def _unpack_byte(self, n: int) -> Tuple[Any, ...]:
        # Size 1 -> big-endian unsigned char
        # Size 2 -> big-endian unsigned short
        # Size 4 -> big-endian unsigned int
        # Size 8 -> big-endian unsigned long long
        formats: Dict[int, str] = {1: '>B', 2: '>H', 4: '>I', 8: '>Q'}
        return unpack(formats[n], self.mpls.read(n))


class MoviePlaylist(MplsObject):
    """https://github.com/lw/BluRay/wiki/MPLS"""
    type_indicator: str
    version_number: str
    playlist_start_address: int
    playlist_mark_start_address: int
    extension_data_start_address: int

    def load(self):
        pos = self._get_pos()

        if pos != 0:
            raise Exception('MoviePlaylist: You should called it at the start of the mpls file!')

        self.type_indicator = self.mpls.read(4).decode('utf-8')                 # 4 bytes - 32 bits
        self.version_number = self.mpls.read(4).decode('utf-8')                 # 4 bytes - 32 bits
        self.playlist_start_address, = self._unpack_byte(4)                     # 4 bytes - 32 bits
        self.playlist_mark_start_address, = self._unpack_byte(4)                # 4 bytes - 32 bits
        self.extension_data_start_address, = self._unpack_byte(4)               # 4 bytes - 32 bits
        self.mpls.read(20)                                                      # 20 bytes - 160 bits - Reserved

        return self
