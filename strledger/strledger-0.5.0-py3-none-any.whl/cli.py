import base64
import sys
from typing import Callable, Any
from urllib.parse import urljoin

import click
from ledgerwallet import __version__ as ledger_wallet_version
from ledgerwallet import utils
from ledgerwallet.client import CommException
from stellar_sdk import (
    Network,
    parse_transaction_envelope_from_xdr,
    Server,
    TransactionEnvelope,
    FeeBumpTransactionEnvelope,
)
from stellar_sdk.exceptions import BaseRequestError
from stellar_sdk import __version__ as stellar_sdk_version
from strledger import __issue__
from strledger import __version__ as strledger_version
from strledger.core import (
    SW,
    StrLedger,
    DEFAULT_KEYPAIR_INDEX,
    get_default_client,
    DeviceNotFoundException,
)

_DEFAULT_HORIZON_SERVER_URL = "https://horizon.stellar.org"


def echo_normal(message: str) -> None:
    click.echo(message)


def echo_success(message: str) -> None:
    click.echo(click.style(message, fg="green"))


def echo_error(message: Any) -> None:
    click.echo(click.style(message, fg="red"), err=True)


@click.group()
@click.option("-v", "--verbose", is_flag=True, help="Display exchanged APDU.")
@click.pass_context
def cli(ctx, verbose):
    """Stellar Ledger commands.

    This project is built on the basis of ledgerctl,
    you can check ledgerctl for more features.
    """

    if verbose:
        utils.enable_apdu_log()

    def get_client() -> StrLedger:
        try:
            return get_default_client()
        except DeviceNotFoundException:
            echo_error("No Ledger device has been found.")
            sys.exit(1)

    ctx.obj = get_client


@cli.command(name="app-info")
@click.pass_obj
def get_app_info(get_client: Callable[[], StrLedger]) -> None:
    """Get Stellar app info."""
    client = get_client()
    data = client.get_app_info()
    echo_success(f"Stellar App Version: {data.version}")
    enabled = "Yes" if data.hash_signing_enabled else "No"
    echo_success(f"Hash Signing Enabled: {enabled}")


@cli.command(name="sign-tx")
@click.option(
    "-n",
    "--network-passphrase",
    default=Network.PUBLIC_NETWORK_PASSPHRASE,
    required=False,
    help="Network passphrase (blank for public network).",
)
@click.option(
    "-i",
    "--keypair-index",
    type=int,
    required=False,
    help="Keypair Index.",
    default=DEFAULT_KEYPAIR_INDEX,
    show_default=True,
)
@click.option("-s", "--submit", is_flag=True, help="Submit to Stellar Network.")
@click.option(
    "-u",
    "--horizon-url",
    type=str,
    required=False,
    help="Horizon Server URL.",
    default=_DEFAULT_HORIZON_SERVER_URL,
    show_default=True,
)
@click.argument("transaction_envelope")
@click.pass_obj
def sign_transaction(
    get_client: Callable[[], StrLedger],
    network_passphrase: str,
    transaction_envelope: str,
    keypair_index: int,
    submit: bool,
    horizon_url: str,
):
    """Sign a base64-encoded transaction envelope.

    For testnet transactions, use the following network passphrase:
    'Test SDF Network ; September 2015'
    """
    client = get_client()
    try:
        te = parse_transaction_envelope_from_xdr(
            xdr=transaction_envelope, network_passphrase=network_passphrase
        )
    except Exception:
        echo_error(
            "Failed to parse XDR.\n"
            "Make sure to pass a valid base64-encoded transaction envelope.\n"
            "You can check whether the data you submitted is valid "
            "through XDR Viewer - https://laboratory.stellar.org/#xdr-viewer"
        )
        sys.exit(1)
    tx_hash = te.hash_hex()
    echo_normal(f"Network Passphrase: {network_passphrase}")
    echo_normal(f"Transaction Hash: {tx_hash}")
    echo_normal("Please confirm this transaction on Ledger.")

    try:
        assert isinstance(te, (TransactionEnvelope, FeeBumpTransactionEnvelope))
        client.sign_transaction(transaction_envelope=te, keypair_index=keypair_index)
    except CommException as e:
        if e.sw == SW.DENY:
            echo_error("The request to sign the transaction was denied.")
        elif e.sw == SW.UNKNOWN_OP:
            echo_error("The transaction contains unsupported operation(s).")
        elif e.sw == SW.UNKNOWN_ENVELOPE_TYPE:
            echo_error(
                "The transaction contains unsupported transaction envelope type."
            )
        else:
            echo_error(f"Unknown exception, you can the problem here: {__issue__}")
            raise
        sys.exit(1)

    echo_success("Signed successfully.")
    echo_success("Base64-encoded signed transaction envelope:")
    echo_success(te.to_xdr())
    if submit:
        echo_normal("Submitting to the network...")
        server = Server(horizon_url)
        try:
            server.submit_transaction(te)
        except BaseRequestError as e:
            echo_error("submit failed, error info:")
            echo_error(e)
            sys.exit(1)

        echo_success(f"Successfully submitted.")
        if network_passphrase == Network.PUBLIC_NETWORK_PASSPHRASE:
            url = f"https://stellar.expert/explorer/public/tx/{tx_hash}"
        elif network_passphrase == Network.TESTNET_NETWORK_PASSPHRASE:
            url = f"https://stellar.expert/explorer/testnet/tx/{tx_hash}"
        else:
            url = urljoin(horizon_url, f"/transactions/{tx_hash}")
        echo_success(f"Stellar Explorer: {url}")


@cli.command(name="sign-tx-hash")
@click.option(
    "-i",
    "--keypair-index",
    type=int,
    required=False,
    help="Keypair Index.",
    default=DEFAULT_KEYPAIR_INDEX,
    show_default=True,
)
@click.argument("transaction_hash")
@click.pass_obj
def sign_transaction_hash(
    get_client: Callable[[], StrLedger],
    transaction_hash: str,
    keypair_index: int,
):
    """Sign a hex encoded transaction hash."""
    client = get_client()
    try:
        signature = client.sign_transaction_hash(transaction_hash, keypair_index)
    except CommException as e:
        if e.sw == SW.TX_HASH_SIGNING_MODE_NOT_ENABLED:
            echo_error(
                "Hash signing is not enabled on this device.\n"
                "Please enable it on the device and try again."
            )
        elif e.sw == SW.DENY:
            echo_error("The request to sign the transaction hash was denied.")
            sys.exit(1)
        else:
            raise e
    signature_base64 = base64.b64encode(signature).decode()
    echo_success(signature_base64)


@cli.command(name="get-address")
@click.option(
    "-i",
    "--keypair-index",
    type=int,
    required=False,
    help="Keypair Index.",
    default=DEFAULT_KEYPAIR_INDEX,
    show_default=True,
)
@click.option("-c", "--confirm", is_flag=True, help="Confirm address on the device.")
@click.pass_obj
def get_address(
    get_client: Callable[[], StrLedger], keypair_index: int, confirm: bool
) -> None:
    """Get Stellar public address."""
    client = get_client()
    try:
        keypair = client.get_keypair(keypair_index, confirm)
    except CommException as e:
        if e.sw == SW.DENY:
            echo_error("The request to confirm the address was denied.")
            sys.exit(1)
        else:
            raise e
    echo_success(keypair.public_key)


@cli.command(name="version")
def version() -> None:
    """Get strledger version info."""
    echo_success(f"StrLedger Version: {strledger_version}")
    echo_success(f"Ledger Wallet Version: {ledger_wallet_version}")
    echo_success(f"Stellar SDK Version: {stellar_sdk_version}")


if __name__ == "__main__":
    cli()
