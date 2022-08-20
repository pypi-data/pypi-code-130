from pathlib import Path

import pandas as pd

from recanime.anime_store.store import AnimeStore


class ExcelAnimeStore(AnimeStore):
    def __init__(self, excel_path: Path) -> None:
        """Overwrite the init method"""

        self.anime_df = pd.read_csv(
            excel_path,
            low_memory=False,
            usecols=["MAL_ID", "Name", "Genres", "synopsis"],
            dtype={"MAL_ID": "string"}
        )
        self.anime_df.rename({"MAL_ID": "anime_id"}, inplace=True, axis=1)
        self.anime_df.rename({"Name": "anime_name"}, inplace=True, axis=1)
        self.anime_df.rename({"Genres": "genres"}, inplace=True, axis=1)

        self.anime_df['genres'] = self.anime_df['genres'].str.split(pat=",", expand=False)
        self.anime_df['genres'] = self.anime_df['genres'].apply(
            lambda genres: [genre.strip() for genre in genres]
        )
