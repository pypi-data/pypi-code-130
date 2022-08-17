import os
from dotenv import load_dotenv


class MongoKeys():
    """
    Static Class to get .env variables for MongoDB Authentication.
    """
    load_dotenv()

    @staticmethod
    def get_cluster_name():
        return os.environ.get('CLUSTER_NAME')

    @staticmethod
    def get_cluster_password():
        return os.environ.get('CLUSTER_PASSWORD')


class TwitterKeys():
    # Initialize dotenv within class call
    load_dotenv()
    """
    Static Class to get .env variables for Twitter API Developer safely.
    """
    @staticmethod
    def get_API_KEY():
        load_dotenv()
        """Returns Twitter Developer API_KEY"""
        return os.environ.get('API_KEY')

    @staticmethod
    def get_API_KEY_SECRET():
        load_dotenv()
        """Returns Twitter Developer API_KEY_SECRET"""
        return os.environ.get('API_KEY_SECRET')

    @staticmethod
    def get_BEARER_TOKEN():
        load_dotenv()
        """Returns Twitter Developer BEARER_TOKEN"""
        return os.environ.get('BEARER_TOKEN')

    @staticmethod
    def get_LITTLE_T_ACCESS_TOKEN():
        load_dotenv()
        """Returns Twitter Developer ACCESS_TOKEN"""
        return os.environ.get('LITTLE_T_TOKEN')

    @staticmethod
    def get_LITTLE_T_ACCESS_TOKEN_SECRET():
        load_dotenv()
        """Returns Twitter Developer ACCESS_TOKEN_SECRET"""
        return os.environ.get('LITTLE_T_TOKEN_SECRET')

    @staticmethod
    def get_PROJECT_ACCESS_TOKEN():
        load_dotenv()
        """Returns Twitter Developer ACCESS_TOKEN_SECRET"""
        return os.environ.get('PROJECT_ACCESS_TOKEN')

    @staticmethod
    def get_PROJECT_ACCESS_TOKEN_SECRET():
        load_dotenv()
        """Returns Twitter Developer ACCESS_TOKEN_SECRET"""
        return os.environ.get('PROJECT_ACCESS_TOKEN_SECRET')


if __name__ == '__main__':
    print(TwitterKeys.get_BEARER_TOKEN())
