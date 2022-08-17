"""DAO of user."""
from typing import Optional

from pydantic import validator

from whist_core.error.player_error import NegativeRatingError
from whist_core.user.user import User


class Player(User):
    """
    This is the server side class of an user.
    """
    games: int = 0
    rating: int

    def __str__(self):
        return self.username

    def __hash__(self):
        return hash(self.username)

    def __eq__(self, other):
        if not isinstance(other, Player):
            return False
        return other.username == self.username

    # Pydantic will convert this into a classmethod, cls is the correct parameter
    @validator('rating')
    # noinspection ImproperFirstParameter
    def rating_must_not_be_negative(cls, value):  # pylint: disable=no-self-argument
        """
        Validates the rating. It must be zero or positive.
        """
        if value < 0:
            raise NegativeRatingError()
        return value

    @staticmethod
    def get_player(database: dict, username: str) -> Optional['Player']:
        """
        Returns a player for a given username if they are in the given database.
        :param database: where to look for the user
        :type database: dictionary
        :param username: the name of the user to look for
        :type username: string
        :return: The player instance or None
        :rtype: Player or None
        """
        if username in database:
            return database[username]
        return None
