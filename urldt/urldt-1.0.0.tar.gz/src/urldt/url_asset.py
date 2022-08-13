class URLAsset:
    def __init__(self, csv_head: list) -> None:
        self.url_index = csv_head.index('url')
        self.title_index = csv_head.index('title')
