# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['xklb']

package_data = \
{'': ['*']}

install_requires = \
['catt',
 'ffmpeg-python',
 'humanize',
 'ipython',
 'joblib',
 'mutagen',
 'natsort',
 'pandas',
 'protobuf<4',
 'psutil>=5.9.1,<6.0.0',
 'rich',
 'sqlite-utils',
 'subliminal',
 'tabulate',
 'tinytag']

entry_points = \
{'console_scripts': ['lb = xklb.lb:main',
                     'lt = xklb.lb:listen',
                     'tl = xklb.lb:tube_listen',
                     'tw = xklb.lb:tube_watch',
                     'wt = xklb.lb:watch']}

setup_kwargs = {
    'name': 'xklb',
    'version': '1.12.68',
    'description': 'xk library',
    'long_description': '# lb: xk media library\n\nA wise philosopher once told me, "[The future is autotainment](https://www.youtube.com/watch?v=F9sZFrsjPp0)".\n\nRequires `ffmpeg`\n\n## Install\n\n    pip install xklb\n\n## Quick Start -- filesystem\n\n### 1. Extract Metadata\n\nFor thirty terabytes of video the initial scan takes about four hours to complete. After that, rescans of the same path (or any subpaths) are much quicker--only new files will be read by `ffprobe`.\n\n    lb extract tv.db ./video/folder/\n\n![termtosvg](./examples/extract.svg)\n\n### 2. Watch / Listen from local files\n\n    wt tv.db                          # the default post-action is to do nothing after playing\n    wt tv.db --post-action delete     # delete file after playing\n    lt finalists.db --post-action=ask # ask to delete after playing\n\n## Quick Start -- virtual\n\n### 1. Download Metadata\n\nDownload playlist and channel metadata. Break free of the YouTube algo~\n\n    lb tubeadd educational.db https://www.youtube.com/c/BranchEducation/videos\n\n[![termtosvg](./examples/tubeadd.svg "lb tubeadd example")](https://asciinema.org/a/BzplqNj9sCERH3A80GVvwsTTT)\n\nYou can add more than one at a time.\n\n    lb tubeadd maker.db https://www.youtube.com/c/CuriousMarc/videos https://www.youtube.com/c/element14presents/videos/ https://www.youtube.com/c/DIYPerks/videos\n\n![termtosvg](./examples/tubeadd_multi.svg)\n\nAnd you can always add more later--even from different websites.\n\n    lb tubeadd maker.db https://vimeo.com/terburg\n\nTo prevent mistakes the default configuration is to download metadata for only the newest 20,000 videos per playlist/channel.\n\n    lb tubeadd maker.db --yt-dlp-config playlistend=1000\n\nBe aware that there are some YouTube Channels which have many items--for example the TEDx channel has about 180,000 videos. Some channels even have upwards of two million videos. More than you could likely watch in one sitting. On a high-speed connection (>500 Mbps), it can take up to five hours just to download the metadata for 180,000 videos. My advice: start with the 20,000.\n\n#### 1a. Get new videos for saved playlists\n\nTubeupdate will go through all added playlists and fetch metadata of any new videos not previously seen.\n\n    lb tubeupdate\n\n### 2. Watch / Listen from websites\n\n    lb tubewatch maker.db\n\nIf you like this I also have a [web version](https://unli.xyz/eject/)--but this Python version has more features and it can handle a lot more data.\n\n## Things to know\n\nWhen the database file path is not specified, `video.db` will be created / used.\n\n    lb extract ./tv/\n\nThe same for audio: `audio.db` will be created / used.\n\n    lb extract --audio ./music/\n\nLikewise, `fs.db` from:\n\n    lb extract --filesystem /any/path/\n\nIf you want to specify more than one directory you need to mention the db file explicitly.\n\n    lb extract --filesystem one/\n    lb extract --filesystem fs.db one/ two/\n\nOrganize via separate databases.\n\n    lb extract --audio both.db ./audiobooks/ ./podcasts/\n    lb extract --audio audiobooks.db ./audiobooks/\n    lb extract --audio podcasts.db ./podcasts/ ./another/more/secret/podcasts_folder/\n\n## Usage\n\n### Repeat\n\n    lt                  # listen to 120 random songs (DEFAULT_PLAY_QUEUE)\n    lt --limit 5        # listen to FIVE songs\n    lt -l inf -u random # listen to random songs indefinitely\n    lt -s infinite      # listen to songs from the band infinite\n\n### Watch longest videos\n\n    wt tv.db --sort duration desc\n\n### Watch specific video series in order\n\n    wt tv.db --search \'title of series\' --play-in-order\n\nThere are multiple strictness levels of --play-in-order. If things aren\'t playing in order try adding more `O`s\n\n    wt tv.db --search \'title of series\' -O    # default\n    wt tv.db --search \'title of series\' -OO   # slower, more complex algorithm\n    wt tv.db --search \'title of series\' -OOO  # most strict\n\n### See how many corrupt videos you have\n\n    lb wt -w \'duration is null\' -p a\n\n### Listen to OSTs on chromecast groups\n\n    lt -cast -cast-to \'Office pair\' -s \'  ost\'\n\n### Exercise and watch TV that doesn\'t have subtitles\n\n    wt -u priority -w subtitle_count=0\n\n### Print a list of files below a 1280px resolution\n\n    wt -w \'width<1280\' -p f\n\n### Play files under a certain throughput\n\nI don\'t save bitrate information (if enough people request then I\'ll add it) but for now you can use file size and duration as a proxy\n\n    wt -w \'size/duration<50000\'\n\n### Check if you\'ve downloaded something before\n\n    wt -u duration --print -s \'video title\'\n\n### View how much time you have listened to music\n\n    lb lt -w play_count\'>\'0 -p a\n\n### See how much video you have\n\n    lb wt video.db -p a\n    ╒═══════════╤═════════╤═════════╤═════════╕\n    │ path      │   hours │ size    │   count │\n    ╞═══════════╪═════════╪═════════╪═════════╡\n    │ Aggregate │  145769 │ 37.6 TB │  439939 │\n    ╘═══════════╧═════════╧═════════╧═════════╛\n    Total duration: 16 years, 7 months, 19 days, 17 hours and 25 minutes\n\n### Search the filesystem\n\nYou can also use `lb` for any files:\n\n    $ lb extract -fs ~/d/41_8bit/\n\n    $ lb fs fs.db -p a -s mario luigi\n    ╒═══════════╤══════════════╤══════════╤═════════╕\n    │ path      │   sparseness │ size     │   count │\n    ╞═══════════╪══════════════╪══════════╪═════════╡\n    │ Aggregate │            1 │ 215.0 MB │       7 │\n    ╘═══════════╧══════════════╧══════════╧═════════╛\n\n    $ lb fs -p -s mario -s luigi -s jpg -w is_dir=0 -u \'size desc\'\n    ╒═══════════════════════════════════════╤══════════════╤═════════╕\n    │ path                                  │   sparseness │ size    │\n    ╞═══════════════════════════════════════╪══════════════╪═════════╡\n    │ /mnt/d/41_8bit/roms/gba/media/images/ │      1.05632 │ 58.2 kB │\n    │ Mario & Luigi - Superstar Saga (USA,  │              │         │\n    │ Australia).jpg                        │              │         │\n    ├───────────────────────────────────────┼──────────────┼─────────┤\n    │ /mnt/d/41_8bit/roms/gba/media/box3d/M │      1.01583 │ 44.4 kB │\n    │ ario & Luigi - Superstar Saga (USA,   │              │         │\n    │ Australia).jpg                        │              │         │\n    ╘═══════════════════════════════════════╧══════════════╧═════════╛\n\n### You can pipe stuff\n\n[lowcharts](https://github.com/juan-leon/lowcharts)\n\n    $ wt-dev -p f -col time_created | lowcharts timehist -w 80\n    Matches: 445183.\n    Each ∎ represents a count of 1896\n    [2022-04-13 03:16:05] [151689] ∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎\n    [2022-04-19 07:59:37] [ 16093] ∎∎∎∎∎∎∎∎\n    [2022-04-25 12:43:09] [ 12019] ∎∎∎∎∎∎\n    [2022-05-01 17:26:41] [ 48817] ∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎\n    [2022-05-07 22:10:14] [ 36259] ∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎\n    [2022-05-14 02:53:46] [  3942] ∎∎\n    [2022-05-20 07:37:18] [  2371] ∎\n    [2022-05-26 12:20:50] [   517]\n    [2022-06-01 17:04:23] [  4845] ∎∎\n    [2022-06-07 21:47:55] [  2340] ∎\n    [2022-06-14 02:31:27] [   563]\n    [2022-06-20 07:14:59] [ 13836] ∎∎∎∎∎∎∎\n    [2022-06-26 11:58:32] [  1905] ∎\n    [2022-07-02 16:42:04] [  1269]\n    [2022-07-08 21:25:36] [  3062] ∎\n    [2022-07-15 02:09:08] [  9192] ∎∎∎∎\n    [2022-07-21 06:52:41] [ 11955] ∎∎∎∎∎∎\n    [2022-07-27 11:36:13] [ 50938] ∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎\n    [2022-08-02 16:19:45] [ 70973] ∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎\n    [2022-08-08 21:03:17] [  2598] ∎\n\n![video width](https://user-images.githubusercontent.com/7908073/184737808-b96fbe65-a1d9-43c2-b6b4-4bdfab592190.png)\n\n![fps](https://user-images.githubusercontent.com/7908073/184738438-ee566a4b-2da0-4e6d-a4b3-9bfca036aa2a.png)\n\n\n### TODO\n\n- all: more test coverage\n- all: Documentation in wiki\n- all: investigate fts using sqlite-utils\n- all: automatic drop low value indexes? (reduce db size)\n- tube: why nan instead of null ?\n- tube: sqlite-utils create-index\n- tube: Download subtitle to embed in db tags for search\n- fs: split_by_silence without modifying files\n- fs: is_deleted? mixed feelings\n',
    'author': 'Jacob Chapman',
    'author_email': '7908073+chapmanjacobd@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
