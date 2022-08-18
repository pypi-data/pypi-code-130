# -*- coding: utf-8 -*-
"""
    [Hashing]
"""

from passlib.context import CryptContext

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Password:
    def hash(password: str):
        """[Password to Hash]"""
        return password_context.hash(password)

    def verify(input_plain_password: str, hashed_password: str):
        """[Verify Password]

        Args:
            input_plain_password (str): Input from user.
            hashed_password (str): Password stored in the database.

        Returns:
            bool: Is a valid password? (True or False).
        """

        return password_context.verify(input_plain_password, hashed_password)
