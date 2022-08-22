from pathlib import Path

import pandas as pd


class Cache:
    @property
    def output_path(self):
        if self.locale == 'local':
            result = Path.home() / ".lwdp_cache"
            result.mkdir(exist_ok=True)
            return result
        else:
            raise NotImplementedError("Anything other than local cacheing not implemented")

    def __init__(self, locale: str = 'local', format: str = 'csv'):
        self.locale = locale
        self.format = format

    def read(self, path: Path):
        full_path = self.output_path / path
        if full_path.exists():
            return pd.read_csv(full_path)
        else:
            return None

    def write(self, pdf: pd.DataFrame, path: Path):
        pdf.to_csv(self.output_path / path)
