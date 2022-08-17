import unittest
from src.leo_landau_SDK.api_request import ApiRequest
from src.leo_landau_SDK.movie import Movie
import os
from dotenv import load_dotenv
load_dotenv()
# access token is in .env file
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")

# https://docs.python.org/3/library/unittest.html

class TestMovieMethods(unittest.TestCase):

    def test_num_movies(self):
        api_request = ApiRequest(Movie, ACCESS_TOKEN)
        api_result = api_request.get_all()
        print(f"num movies: {api_result.total}")
        self.assertEqual(api_result.total, 8)

    def test_get_single_movie(self):
        api_request = ApiRequest(Movie, ACCESS_TOKEN)
        movie_id = "5cd95395de30eff6ebccde5c"
        api_result = api_request.get(movie_id)
        self.assertEqual(api_result.total, 1)

    def test_movie_filter(self):
        api_request = ApiRequest(Movie, ACCESS_TOKEN)
        filter_str = "runtimeInMinutes>=160"
        api_request.filter(filter_str)
        api_result = api_request.get()
        movies = api_result.docs
        num_movies = len(movies)
        self.assertEqual(num_movies, 7)

    def test_movie_filter_1(self):
        api_request = ApiRequest(Movie, ACCESS_TOKEN)
        filter_str = "academyAwardWins>0"
        api_request.filter(filter_str)
        api_result = api_request.get()
        movies = api_result.docs
        num_movies = len(movies)
        self.assertEqual(num_movies, 6)

if __name__ == '__main__':
    unittest.main()
