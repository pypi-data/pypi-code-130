"""Exceptions that occur in player or user"""


class NegativeRatingError(Exception):
    """
    Is raised if an attempt is made to assign a negative rating to a player.
    """
