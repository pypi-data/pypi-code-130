import sys
import click

from .solana import get_rpc


@click.group()
@click.version_option("1.0.0")
def main():
    """Utilitys for Solana NFTs"""
    pass


@main.command()
@click.option('--amount', prompt='How many white list tokens would you like to mint?', type=int)
@click.option('--cluster', prompt=True, default=get_rpc())
def create_whitelist_token(amount, cluster):
    """Search through CVE Database for vulnerabilities"""
    create_whitelist_token(amount, cluster)


if __name__ == '__main__':
    args = sys.argv
    if "--help" in args or len(args) == 1:
        print("Please enter a command!")
    main()
