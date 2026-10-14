# muska-signage-media

Posters and playlists for the Muska counter screens. This repo is **public** on purpose:
the screens download from it, so never put anything private here.

    source/<screen>/      your original pictures (any size)
    screens/<screen>/     what the screens download: playlist.txt + converted posters
    previews/<screen>/    small pictures showing roughly how the real e-paper will look
    tools/                build_media.py (convert), publish.sh (convert + upload)

Screens: `13in3-a` and `13in3-b` (13.3" colour, portrait), `7in5` (7.5" black & white).
Need another 13.3" screen? Make folders `source/13in3-c` and `screens/13in3-c` (copy a
playlist.txt), then set DEVICE_ID "13in3-c" in that board's config.h.

Day to day: copy pictures into `source/13in3-a/`, edit `screens/13in3-a/playlist.txt`,
then run `sh tools/publish.sh`.  Full instructions: see the README in the firmware folder.
