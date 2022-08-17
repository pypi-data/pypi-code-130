import unittest
from src.leo_landau_SDK.api_request import ApiRequest
from src.leo_landau_SDK.character_quote import CharacterQuote
from src.leo_landau_SDK.movie_quote import MovieQuote
from src.leo_landau_SDK.quote import Quote
import os
from dotenv import load_dotenv

load_dotenv()
# access token is in .env file
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")

# https://docs.python.org/3/library/unittest.html

class TestQuoteMethods(unittest.TestCase):

    def test_movie_quotes(self):
        api_request = ApiRequest(MovieQuote, ACCESS_TOKEN)
        movie_id = "5cd95395de30eff6ebccde5c"
        api_result = api_request.get(movie_id)
        self.assertEqual(api_result.total, 507)

    def test_character_quotes(self):
        api_request = ApiRequest(CharacterQuote, ACCESS_TOKEN)
        character_id = "5cd99d4bde30eff6ebccfea0"
        api_result = api_request.get(character_id)
        self.assertEqual(api_result.total, 216)

    def test_all_quotes(self):
        api_request = ApiRequest(Quote, ACCESS_TOKEN)
        api_result = api_request.get_all()
        self.assertEqual(api_result.total, 2390)

    def test_single_quote(self):
        api_request = ApiRequest(Quote, ACCESS_TOKEN)
        quote_id = "5cd96e05de30eff6ebcce8c7"
        api_result = api_request.get(quote_id)
        quotes = api_result.docs
        self.assertEqual(api_result.total, 1)
        self.assertEqual(len(quotes), 1)

    def test_quote_sort_desc(self):
        api_request = ApiRequest(Quote, ACCESS_TOKEN)
        api_request.limit(1)
        api_request.sort_by("dialog", "desc")
        api_result = api_request.get()
        quote = api_result.docs[0]
        expected_dialog = "well, yes. At least well enough for my own people. But we have no songs for great halls and evil times."
        self.assertEqual(quote.dialog, expected_dialog)

    def test_quote_sort_asc(self):
        api_request = ApiRequest(Quote, ACCESS_TOKEN)
        api_request.limit(20)
        api_request.sort_by("dialog")
        api_result = api_request.get()
        quote = api_result.docs[19]
        expected_dialog = "...which is, of course, ridiculous."
        self.assertEqual(quote.dialog, expected_dialog)


if __name__ == '__main__':
    unittest.main()
