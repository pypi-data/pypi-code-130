import re
import warnings
import functools

# TODO: remove pylint disable, once we require python >= 3.9
from os import PathLike  # pylint: disable=unused-import
from typing import Iterable, Iterator, Optional, Union

import gpg_lite as gpg

from .archive import archive_reader
from .metadata import METADATA_FILE_SIG, METADATA_FILE

DEFAULT_URL_OPENER = gpg.keyserver.DEFAULT_URL_OPENER
URL_OPENER_TYPE = gpg.keyserver.UrlOpener


def pgp_key_as_str(key: gpg.Key, full_fingerprint: bool = True) -> str:
    """Return the PGP key in the form of a string."""
    key_user_id = key.uids[0]
    return (
        f"{key_user_id.full_name} <{key_user_id.email}> "
        f"[{key.fingerprint if full_fingerprint else key.key_id}]"
    )


def assert_is_pgp_fingerprint(str_to_test: str) -> None:
    """Raise an error if the input string is not a valid PGP key fingerprint."""
    if not re.fullmatch(r"^[a-fA-F0-9]{40}$", str_to_test):
        raise RuntimeError("Invalid fingerprint")


def assert_key_not_revoked(key: gpg.Key) -> None:
    """Check that a PGP key has not been revoked by its owner.

    :param key: GnuPG key to validate.
    :raises RuntimeError: error is raised if the key is revoked.
    """
    if key.validity is gpg.Validity.revoked:
        raise RuntimeError(f"{key.uids[0]} key has been revoked")


def download_key_by_fingerprint(
    fingerprint: str,
    gpg_store: gpg.GPGStore,
    keyserver_url: str,
    sigs: bool = True,
    url_opener: URL_OPENER_TYPE = DEFAULT_URL_OPENER,
) -> gpg.Key:
    """Download a single PGP key specified via its fingerprint.

    The key is downloaded from the specified `keyserver_url` and is returned
    as a gpg-lite Key object.

    An error is raised if:
     * A bad fingerprint is passed.
     * No key matching the fingerprint is found on the keyserver.
     * The keyserver cannot be reached.
     * The key fails to download/import for an unknown reason.

    :param fingerprint: fingerprint of key to download. Must be exactly 40
        hexadecimal chars long.
    :param gpg_store: instance of a gpg-lite GPGStore object.
    :param keyserver_url: URL of keyserver from where to download the key.
    :param sigs: if True, the key is returned with its signatures.
    :param url_opener: optional URL opener to allow proxying.
    :returns: gpg-lite Key instance.
    :raises RuntimeError:
    """

    error_prefix = f"Download of key [{fingerprint}] from [{keyserver_url}] failed: "
    try:
        assert_is_pgp_fingerprint(fingerprint)
        gpg_store.vks_recv_key(
            identifier=fingerprint, keyserver=keyserver_url, url_opener=url_opener
        )
    except (
        gpg.KeyserverError,
        gpg.KeyserverKeyNotFoundError,
        gpg.KeyserverOtherError,
        RuntimeError,
    ) as e:
        raise RuntimeError(error_prefix + str(e)) from e

    # Load the newly downloaded key from the user's local keyring.
    (key,) = gpg_store.list_pub_keys(search_terms=(fingerprint,), sigs=sigs)
    return key


def retrieve_and_refresh_key(
    key_identifier: str,
    gpg_store: gpg.GPGStore,
    keyserver_url: Optional[str] = None,
    allow_key_download: bool = True,
    url_opener: URL_OPENER_TYPE = DEFAULT_URL_OPENER,
) -> gpg.Key:
    """Retrieve a public PGP key from a user's local keyring based on its
    fingerprint, long key ID or email.

    If the key is not available locally, an attempt to download it from the
    specified keyserver is made, but only if the key_identifier is a full
    fingerprints - no auto-download of keys is performed for keys identified
    by their long key ID or email.

    Exactly one key is returned. An error is raised if a given identifier
    returns multiple or no keys.

    Summary of performed tasks:
     - Retrieve key from local keyring, or download missing key from the
       keyserver.
     - Refresh local copy of key by re-downloading if from keyserver.
     - Verify that key is not revoked by its owner.

    :param key_identifier: fingerprint, key ID or email of key to retrieve.
    :param gpg_store: key database as gnupg object.
    :param keyserver_url: URL of keyserver for key download/refresh.
    :param allow_key_download: if True (the default), PGP keys are attempted to
        be downloaded (if missing in local keyring) or refreshed (if present)
        from the specified keyserver (if any). If False, download and refresh
        of keys is disabled, even if a keyserver is specified.
    :param url_opener: optional URL opener to allow proxying.
    :return: Iterator with the retrieved keys as gpg.Key objects.
    :raise RuntimeError: Raised if no key is found for one or more of the
        search_terms, or if multiple keys are found for a given identifier.
    """
    download_key = functools.partial(
        download_key_by_fingerprint,
        gpg_store=gpg_store,
        keyserver_url=keyserver_url,
        sigs=True,
        url_opener=url_opener,
    )

    keys = list(gpg_store.list_pub_keys(search_terms=(key_identifier,), sigs=True))

    # Case 1: the key is already present in the local keyring: an attempt
    # is made to refresh it (i.e. re-download it from the keyserver).
    if len(keys) == 1:
        key = keys[0]
        if allow_key_download and keyserver_url:
            try:
                key = download_key(fingerprint=key.fingerprint)
            except RuntimeError:
                warnings.warn(f"Key could not be refreshed: {pgp_key_as_str(key)}")

    # Case 2: key is not present in local keyring. If the key was specified
    # via its full fingerprint, an attempt is made to download it from the
    # specified keyserver.
    elif not keys:
        error_prefix = f"Key [{key_identifier}] was not found in local keyring"
        try:
            assert_is_pgp_fingerprint(key_identifier)
        except RuntimeError:
            raise RuntimeError(
                f"{error_prefix} and only keys specified via their full "
                "fingerprint can be auto-downloaded."
            ) from None
        if not allow_key_download:
            raise RuntimeError(error_prefix + " and key download is disabled.")
        if not keyserver_url:
            raise RuntimeError(error_prefix + " and no keyserver URL is provided.")
        key = download_key(fingerprint=key_identifier)

    # If more than one key is matching the search term, raise an error.
    else:
        raise RuntimeError(
            "Ambiguous input: more than one key in your local keyring "
            f"matches with [{key_identifier}]. This problem can be "
            "solved by using key fingerprints as search terms."
        )

    # Verify that the key is not revoked by its owner.
    assert_key_not_revoked(key=key)
    return key


def retrieve_and_refresh_keys(
    key_identifiers: Iterable[str],
    gpg_store: gpg.GPGStore,
    keyserver_url: Optional[str] = None,
    allow_key_download: bool = True,
    url_opener: URL_OPENER_TYPE = DEFAULT_URL_OPENER,
) -> Iterator[gpg.Key]:
    """Wrapper around retrieve_and_refresh_key for multiple keys at once.

    Keys are returned in the same order as requested (i.e. order of elements
    in `key_identifiers`). Argument description, see retrieve_and_refresh_key.
    """
    yield from (
        retrieve_and_refresh_key(
            identifier, gpg_store, keyserver_url, allow_key_download, url_opener
        )
        for identifier in key_identifiers
    )


# pylint: disable=too-many-locals
def verify_metadata_signature(
    tar_file: Union[
        str, "PathLike[str]"
    ],  # TODO: unquote type-hint, once we require python >= 3.9
    gpg_store: gpg.GPGStore,
    signee_fingerprint: Optional[str] = None,
    keyserver_url: Optional[str] = None,
    allow_key_download: bool = True,
    url_opener: URL_OPENER_TYPE = DEFAULT_URL_OPENER,
) -> None:
    """Verify that an archive file contains a metadata file that is signed by
    the expected (and valid) PGP key.

    If the signee key is absent from the user's local keyring, its download
    from a keyserver (if specified) is attempted. If the key is already
    present in the keyring, its refresh from the specified keyserver is
    attempted.

    The function raises an error if any of the checks fails.

    :param tar_file: archive file (zip/tar) containing a signature to check.
    :param gpg_store: PGP keyring as gpg-lite GPGStore object.
    :param signee_fingerprint: if specified, the function verifies that the
        signature on the metadata file matches the specified fingerprint.
    :param keyserver_url: URL of keyserver from where the signee's key should
        be downloaded/refreshed.
    :param allow_key_download: if True (the default), the metadata signee's key
        is attempted to be downloaded (if missing in local keyring) or
        refreshed (if present) from the specified keyserver (if any). If False,
        download and refresh of the signee's key is disabled, even if a
        keyserver is specified.
    :param url_opener: optional URL opener to allow proxying.
    :return: nothing.
    :raise RuntimeError: if the signee's signature doesn't exist or is invalid.
    """

    error_prefix = f"Metadata signature check failed for '{tar_file}'"

    def retrieve_refresh_key(fingerprint: str) -> gpg.Key:
        try:
            return retrieve_and_refresh_key(
                fingerprint, gpg_store, keyserver_url, allow_key_download, url_opener
            )
        except RuntimeError as e:
            raise RuntimeError(f"{error_prefix}: signee's key is invalid. {e}") from e

    # Extract signature and metadata files from the archive file.
    with archive_reader(tar_file) as archive:
        # Retrieve signature from (detached) file.
        try:
            detached_signature = archive.extract_member(METADATA_FILE_SIG).read()
        except (KeyError, ValueError) as e:
            raise RuntimeError(f"{error_prefix}: signature is missing") from e

        # Retrieve metadata file content (needed for signature verification).
        try:
            metadata = archive.extract_member(METADATA_FILE).read()
        except (KeyError, ValueError) as e:
            raise RuntimeError(f"{error_prefix}: metadata is missing") from e

    # Verify that the detached signature file matches with the metadata file,
    # and retrieve the signee's fingerprint.
    try:
        fingerprint = gpg_store.verify_detached_sig(metadata, detached_signature)
    except gpg.GPGError as e:
        raise RuntimeError(f"{error_prefix}: signature is invalid. {e}") from e

    # Download/refresh the PGP key of the signee, check it's not user-revoked.
    signee_key = retrieve_refresh_key(fingerprint)

    # If an expected signee fingerprint was passed, verify that the actual
    # signature fingerprint present on the detached signature file matches it.
    if signee_fingerprint:
        if signee_fingerprint != fingerprint:
            # A mismatch in fingerprints can indicate that the signature was
            # made using a subkey derived from the primary key. To verify if
            # this is the case, we retrieve the full keys and compare them.
            # The search below works because GnuPG is also able to retrieve
            # a key based on one of its subkey fingerprints.
            signee_key_expected = retrieve_refresh_key(signee_fingerprint)
            if signee_key_expected != signee_key:
                raise RuntimeError(
                    f"{error_prefix}: the key '{fingerprint}' used to sign the "
                    "metadata file does not match the key associated with the "
                    f"data sender fingerprint '{signee_fingerprint}' as "
                    "indicated in the metadata file."
                )
