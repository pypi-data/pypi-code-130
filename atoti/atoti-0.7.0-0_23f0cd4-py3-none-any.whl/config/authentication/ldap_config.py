from dataclasses import dataclass

from atoti_core import keyword_only_dataclass

from .._config import Config


@keyword_only_dataclass
@dataclass(frozen=True)
class LdapConfig(Config):
    """The configuration to connect to an `LDAP <https://en.wikipedia.org/wiki/Lightweight_Directory_Access_Protocol>`__ authentication provider.

    The user's roles are defined using :class:`~atoti_plus.security.LdapSecurity`.

    Example:

        >>> auth_config = tt.LdapConfig(
        ...     url="ldap://example.com:389",
        ...     base_dn="dc=example,dc=com",
        ...     user_search_base="ou=people",
        ...     group_search_base="ou=roles",
        ... )
    """

    url: str
    """The LDAP URL including the protocol and port."""

    base_dn: str
    """The Base Distinguished Name of the directory service."""

    user_search_filter: str = "(uid={0})"
    """The LDAP filter used to search for users.

    The substituted parameter is the user's login name.
    """

    user_search_base: str = ""
    """Search base for user searches."""

    group_search_filter: str = "(uniqueMember={0})"
    """The LDAP filter to search for groups.

    The substituted parameter is the DN of the user.
    """

    group_search_base: str = ""
    """The search base for group membership searches."""

    group_role_attribute_name: str = "cn"
    """The attribute name that maps a group to a role."""
