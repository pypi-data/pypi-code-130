import unittest
import os
from dotenv import load_dotenv
from src.leo_landau_SDK.character import Character
from src.leo_landau_SDK.api_request import ApiRequest

load_dotenv()
# access token is in .env file
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")

# https://docs.python.org/3/library/unittest.html

class TestCharacterMethods(unittest.TestCase):

    def test_all_characters(self):
        api_request = ApiRequest(Character, ACCESS_TOKEN)
        api_result = api_request.get_all()
        num_results = len(api_result.docs)
        print(f"num_results: {num_results}")
        self.assertEqual(api_result.total, 933)

    def test_characters_with_limit(self):
        api_request = ApiRequest(Character, ACCESS_TOKEN)
        limit_val = 42
        api_request.limit(limit_val)
        api_result = api_request.get_all()
        num_results = len(api_result.docs)
        print(f"num_results: {num_results}; with limit: {limit_val}")
        self.assertEqual(num_results, limit_val)

    def test_characters_with_page(self):
        api_request = ApiRequest(Character, ACCESS_TOKEN)
        api_request.limit(10)
        api_request.page(2)
        api_result = api_request.get_all()

        page_2_ids = []
        for character in api_result.docs:
            page_2_ids.append(character._id)

        # verify the page_3 ids are not in the page_2_ids list
        api_request.page(3)
        api_result = api_request.get_all()
        for character in api_result.docs:
            self.assertNotIn(character._id, page_2_ids)

    def test_characters_with_offset(self):
        api_request = ApiRequest(Character, ACCESS_TOKEN)
        api_request.limit(10)
        api_request.page(2)
        api_request.offset(2)
        api_result = api_request.get_all()

        page_2_ids = []
        for character in api_result.docs:
            page_2_ids.append(character._id)

        api_request.offset(4)
        api_result = api_request.get_all()

        new_ids = []
        for character in api_result.docs:
            if character._id not in page_2_ids:
                new_ids.append(character._id)

        # how many are new after we modified the offset
        num_new_ids = len(new_ids)

        print(f"num_new_ids: {num_new_ids}; with offset change: {2}")
        self.assertEqual(num_new_ids, 2)

    def test_single_character(self):
        api_request = ApiRequest(Character, ACCESS_TOKEN)
        character_id = "5cdbe47d7ed9587226e7949f"
        api_result = api_request.get(character_id)
        self.assertEqual(api_result.total, 1)

    def test_character_filter(self):
        api_request = ApiRequest(Character, ACCESS_TOKEN)
        filter_str = "name=Gandalf"
        api_request.filter(filter_str)
        api_result = api_request.get()
        characters = api_result.docs
        self.assertEqual(len(characters), 1)

    def test_character_filter_1(self):
        api_request = ApiRequest(Character, ACCESS_TOKEN)
        filter_str = "race=Hobbit,Human"
        api_request.filter(filter_str)
        api_result = api_request.get()
        characters = api_result.docs
        print(f"len(characters): {len(characters)}")
        self.assertEqual(len(characters), 604)

if __name__ == '__main__':
    unittest.main()
