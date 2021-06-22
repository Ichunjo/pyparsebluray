# pyparsebluray

Parse and extract binary data from bluray files

# Installation
```
python -m pip install pyparsebluray
```
or from Github:
```
python -m pip install git+https://github.com/Ichunjo/pyparsebluray.git
```



# Example

```py
import os

from pyparsebluray import mpls

with open('/BD-ROM/BDMV/PLAYLIST/00001.mpls', 'rb') as mpls_file:
    print('_____________Header_____________')
    header = mpls.load_movie_playlist(mpls_file)
    print(header)

    print('_____________AppInfo_____________')
    appinfo = mpls.load_app_info_playlist(mpls_file)
    print(appinfo)

    print('_____________Playlist_____________')
    mpls_file.seek(header.playlist_start_address, os.SEEK_SET)
    pls = mpls.load_playlist(mpls_file)
    print(pls)

    print('_____________Playlist Mark_____________')
    mpls_file.seek(header.playlist_mark_start_address, os.SEEK_SET)
    marks = mpls.load_playlist_mark(mpls_file)
    print(marks)

    print('_____________Extension_____________')
    if header.extension_data_start_address != 0:
        mpls_file.seek(header.extension_data_start_address, os.SEEK_SET)
        extension = mpls.load_extention_data(mpls_file)
        print(extension)

```

# TODO
* Add clpi, index table and movie object


# Credits
* [PyGuymer2](https://github.com/Guymer/PyGuymer)
* [PyGuymer3](https://github.com/Guymer/PyGuymer3)
* [lw](https://github.com/lw/BluRay/wiki/ApplicationFormat)

  
