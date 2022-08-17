# -*- coding: utf-8 -*-
"""
    [Security]
"""

from datetime import datetime, timedelta

from fastberry import Fastberry
from jose import JWTError, jwt

# Config
SETTINGS = Fastberry()
SECRET_KEY = SETTINGS.secret_key
ALGORITHM = "HS256"


class AccessToken:
    """User Access Tokens"""

    @staticmethod
    async def encode(data: dict, expires_delta: timedelta | None = None):
        """[Create Access Token]

        Args:
            data (dict): User's Information.
            expires_delta (timedelta | None, optional) <Defaults to None>: Time for the expiration.

        Returns:
            str: JSON Web Token
        """

        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    async def decode(token: str):
        """[Decode Access Token]

        Args:
            token (str): JSON Web Token

        Returns:
            dict: User's Information.
        """
        if token:
            try:
                return_value = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            except JWTError:
                return_value = {}
        else:
            return_value = {}
        return return_value
