"""Convenience functions"""

__all__ = ['load_movie_playlist', 'load_app_info_playlist', 'load_playlist',
           'load_playlist_mark', 'load_extention_data']

from io import BufferedReader

from .app_info_playlist import AppInfoPlaylist
from .extension_data import ExtensionData
from .movie_playlist import MoviePlaylist
from .playlist import Playlist
from .playlist_mark import PlaylistMarks


def load_movie_playlist(mpls: BufferedReader) -> MoviePlaylist:
    """Loads and returns a MoviePlaylist object"""
    return MoviePlaylist(mpls).load()


def load_app_info_playlist(mpls: BufferedReader) -> AppInfoPlaylist:
    """Loads and returns a AppInfoPlaylist object"""
    return AppInfoPlaylist(mpls).load()


def load_playlist(mpls: BufferedReader) -> Playlist:
    """Loads and returns a Playlist object"""
    return Playlist(mpls).load()


def load_playlist_mark(mpls: BufferedReader) -> PlaylistMarks:
    """Loads and returns a PlaylistMarks object"""
    return PlaylistMarks(mpls).load()


def load_extention_data(mpls: BufferedReader) -> ExtensionData:
    """Loads and returns a ExtensionData object"""
    return ExtensionData(mpls).load()
