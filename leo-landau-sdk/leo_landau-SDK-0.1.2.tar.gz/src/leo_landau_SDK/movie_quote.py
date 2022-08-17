from .quote import Quote


class MovieQuote(Quote):

    @classmethod
    def get_endpoint(cls, movie_id):
        if not movie_id:
            raise RuntimeError("MovieQuote requires movie_id")
        return f"/movie/{movie_id}/quote"

