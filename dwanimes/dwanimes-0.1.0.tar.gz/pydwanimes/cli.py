from argparse import ArgumentParser
import argparse
from pathlib import Path

from pydwanimes.application.players.fembed import Fembed

from pydwanimes.domain import Player
import pydwanimes.application.players.fireload as fireload
import pydwanimes.application.players.your_upload as your_upload
import pydwanimes.application.sites.anime_fenix as anime_fenix
from pydwanimes.application.loading.tqdm_loading import TqdmLoading

players = ("your_upload", "fireload", "fembed")


def main():
    parser = ArgumentParser(description="Anime downloader",
                            formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-n", "--name", dest="name",
                        help="Anime name", required=True)
    parser.add_argument("-c", "--chapter", dest="chapter",
                        type=int, help="Chapter number", required=True)
    parser.add_argument("-d", "--directory",
                        dest="directory", default="static/animes", help="Folder to save animes")
    parser.add_argument("-p", "--player", dest="player",
                        default="your_upload", help="Player to download video")

    args = parser.parse_args()

    anime_slug = args.name
    chapter = args.chapter
    path = Path(args.directory).joinpath(anime_slug)
    player = args.player
    d = path.resolve()

    if not player in players:
        raise KeyError(player)

    ld = TqdmLoading()

    s = anime_fenix.AnimeFenix({
        "directory": d,
        "loading": ld
    })
    s.download_multimedia(anime_slug, chapter)


if __name__ == '__main__':
    main()
