# pyparsebluray

Parse and extract binary data from bluray files


# Example

```py
import os

from pyparsebluray import mpls

with open('/BD-ROM/BDMV/PLAYLIST/00001.mpls', 'rb') as mpls_file:
    header = mpls.load_movie_playlist(mpls_file)
    print(header)

    mpls_file.seek(header.playlist_start_address, os.SEEK_SET)
    pls = mpls.load_playlist(mpls_file)

    print(pls)
```

# TODO
* Add clpi, index table and movie object


# Credits
* [PyGuymer2](https://github.com/Guymer/PyGuymer)
* [PyGuymer3](https://github.com/Guymer/PyGuymer3)
* [lw](https://github.com/lw/BluRay/wiki/ApplicationFormat)

  
