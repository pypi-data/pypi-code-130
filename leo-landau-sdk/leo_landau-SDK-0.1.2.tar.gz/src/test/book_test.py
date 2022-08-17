import unittest
from src.leo_landau_SDK.book import Book
from src.leo_landau_SDK.api_request import ApiRequest
import os
from dotenv import load_dotenv
load_dotenv()
# access token is in .env file
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")

# https://docs.python.org/3/library/unittest.html

class TestBookMethods(unittest.TestCase):

    def test_num_books(self):
        api_request = ApiRequest(Book, ACCESS_TOKEN)
        api_result = api_request.get_result()
        self.assertEqual(api_result.total, 3)

    def test_get_single_book(self):
        api_request = ApiRequest(Book, ACCESS_TOKEN)
        book_id = "5cf5805fb53e011a64671582"
        api_result = api_request.get(book_id)
        self.assertEqual(api_result.total, 1)


if __name__ == '__main__':
    unittest.main()
