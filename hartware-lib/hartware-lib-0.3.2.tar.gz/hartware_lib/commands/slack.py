import argparse

from hartware_lib.adapters.slack import SlackAdapter
from hartware_lib.settings.slack import SlackSettings


def slack_send(command: list = []):
    parser = argparse.ArgumentParser(description="Slack message sender.")
    parser.add_argument("message", help="set the message")
    parser.add_argument("-c", "--channel", help="set the channel")

    args = parser.parse_args(command or None)

    settings = SlackSettings()

    return SlackAdapter(settings).send(message=args.message, channel=args.channel)
