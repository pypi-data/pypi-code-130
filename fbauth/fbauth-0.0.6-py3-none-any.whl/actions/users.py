import datetime
from datetime import timedelta

from fastberry import Fastberry

from .app import ACCESS_TOKEN_EXPIRE_MINUTES, RoleDB, UserDB
from .model import AccountManager, Token
from .security import AccessToken, Password

SETTINGS = Fastberry()


def anonymous_user():
    """Create an Anonymous-User"""
    return AccountManager(
        is_anonymous=True,
        is_authenticated=False,
    )


def get_timestamp():
    """Get TimeStamp"""
    ct = datetime.datetime.now()
    return int(ct.timestamp())


class User:
    users = UserDB
    roles = RoleDB

    @staticmethod
    async def create(
        username: str,
        password: str,
        email: str,
        role_id: int = 1,
        is_super_user: bool = False,
    ):
        """Create Account"""
        input_form = UserDB.form(
            {
                "username": username,
                "password": Password.hash(password),
                "email": email,
                "is_super_user": is_super_user,
            }
        )
        input_form["role_id"] = role_id
        results = await UserDB.create(input_form)
        return results

    @staticmethod
    async def get_by(
        ID: str | None = None,
        username: str | None = None,
        email: str | None = None,
    ):
        """Find Account"""
        # Search
        search_dict = {}
        if ID:
            search_dict["_id"] = ID
        if username:
            search_dict["username"] = username
        elif email:
            search_dict["email"] = email
        # User
        item = await UserDB.get_by(**search_dict)
        # Account Manager
        if item:
            account = AccountManager(
                _id=item._id,
                id=item.id,
                role_id=item.role_id,
                username=item.username,
                email=item.email,
                password=item.password,
                is_disabled=item.is_disabled,
                is_staff=item.is_staff,
                is_super_user=item.is_super_user,
                created_on=item.created_on,
                is_authenticated=True,
            )
        else:
            account = False
        return account

    @classmethod
    async def _authenticate_base(
        cls,
        id: str | None = None,
        username: str | None = None,
        email: str | None = None,
        password: str | None = None,
    ):
        """Authenticate Account"""
        account = await cls.get_by(ID=id, username=username, email=email)
        is_valid = False
        if account:
            is_valid = Password.verify(password, account.password)
        if account and is_valid:
            user = account
        else:
            user = anonymous_user()
        return user

    @classmethod
    async def authenticate(cls, username: str, password: str):
        """Login For Access Token

        Args:
            username (str): User's identification name.
            password (str): User's password.

        Returns:
            Token: (valid: bool, token: str, user: User)
        """

        # Authenticate
        user = await cls._authenticate_base(username=username, password=password)

        # Invalid User
        if not user.is_authenticated:
            return Token(is_valid=False, token=None, user=user)

        # Access Token
        access_token_data = {"sub": str(user._id)}
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = await AccessToken.encode(
            data=access_token_data,
            expires_delta=access_token_expires,
        )

        return Token(is_valid=True, token=access_token, user=user)

    @classmethod
    async def verify_token(cls, token: str):
        """Check Access Token"""
        payload = await AccessToken.decode(token)
        ID: str = payload.get("sub")
        # Expiration Time Check
        expiration: str = payload.get("exp")
        timestamp = get_timestamp()
        # Start
        expired = (expiration < timestamp) if expiration else True
        if expired:
            return Token(is_valid=False, token=None, user=anonymous_user())
        if not ID:
            return Token(is_valid=False, token=None, user=anonymous_user())
        # Get User
        user = await User.get_by(ID=int(ID))
        # Continue ...
        if not user:
            return Token(is_valid=False, token=None, user=anonymous_user())
        return Token(is_valid=True, token=token, user=user)

    @staticmethod
    async def get_perms(role: int = None):
        """Get Role And Check For Permissions"""

        perms = []
        if role:
            item = await RoleDB.get_by(_id=int(role))
            if item:
                found = item.perms or []
                if found and role:
                    perms = found
        return perms
