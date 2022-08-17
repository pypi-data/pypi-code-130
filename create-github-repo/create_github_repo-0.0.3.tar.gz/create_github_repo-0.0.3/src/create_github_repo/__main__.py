#!/usr/bin/env python3

import argparse
import datetime
import json
import logging
import os

import requests

logging.basicConfig(level=logging.INFO, format="%(message)s")


def clparser() -> argparse.ArgumentParser:
    """Create a parser to handle input arguments and displaying.

    a script specific help message.
    """
    desc_msg = """Create a remote repository on GitHub using the command line."""
    parser = argparse.ArgumentParser(
        description=desc_msg,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "repo_name",
        help="Name of the repository to create.",
    )
    parser.add_argument(
        "-f",
        "--auth-file",
        help="File containing GitHub username and token. Expects the username to be on line one and token on line two. Alternative to providing raw username (-u) and token (-t) strings.",
    )
    parser.add_argument(
        "-u",
        "--username",
        help="GitHub username. Alternative to providing a file with authentication information (-f).",
    )
    parser.add_argument(
        "-t",
        "--token",
        help="GitHub token. Alternative to providing a file with authentication information (-f).",
    )

    parser.add_argument(
        "-d",
        "--description",
        dest="description",
        help="Description of the repository.",
    )
    parser.add_argument(
        "-p",
        "--public",
        action="store_true",
        dest="public",
        default=False,
        help="GitHub repository visibility.",
    )
    parser.add_argument(
        "-r",
        "--review",
        action="store_true",
        dest="review",
        default=False,
        help="Verify the transaction and optionally rollback changes.",
    )
    return parser


def parse_auth_file(file: str) -> tuple:
    """Read a file containing authentication information and returns its contents.

    Assumes the username is on line one and token is on line two.

    :file: Path to the file.
    """
    if os.path.exists(file):
        try:
            with open(file, "r", encoding="utf-8") as f:
                auth = f.readlines()
        except Exception as e:
            raise e
    else:
        raise FileExistsError
    try:
        usr = auth[0].strip()
        pwd = auth[1].strip()
    except Exception as e:
        raise e
    return usr, pwd


def response_status(response: requests.models.Response) -> None:
    """Check the status of a response for any errors and.

    print them to the console if any occur.
    """
    if "errors" in json.loads(response.text):
        errors = ""
        for e in json.loads(response.text)["errors"]:
            if errors == "":
                errors = f"{e['message']}"
            else:
                errors = errors + f". {e['message']}"
        raise Exception(
            f"""[{response.status_code}] {json.loads(response.text)['message']}\n
            Error(s): {errors}""",
        )


def delete_repo(url: str, headers: dict) -> None:
    """Send a DELETE request."""
    try:
        requests.delete(url, headers=headers)
    except requests.exceptions.RequestException:
        raise requests.exceptions.RequestException(f"Failed to delete <{url}>")


def review_changes(
    base_url: str,
    repo_name: str,
    username: str,
    token: str,
    response_json: dict,
) -> None:
    """Review the created repository and confirm transaction."""
    logging.info("Attributes:")
    logging.info(f"  visibility: {response_json['visibility']}")
    logging.info(
        f"  created_at: {datetime.datetime.strptime(response_json['created_at'], '%Y-%m-%dT%H:%M:%SZ')}",
    )
    logging.info(f"  description: {response_json['description']}")
    while True:
        revert = input("Do you want to keep these changes [Y/n]: ").strip()
        if not (revert.upper() == "Y" or revert.upper() == "N"):
            logging.warning("Error: please enter [Y] or [n]")
        else:
            if revert.upper() == "N":
                delete_repo(
                    f"{base_url}/repos/{username}/{repo_name}",
                    {"Authorization": f"token {token}"},
                )
                logging.info("Repository deleted.")
            break


def create_new_repo(url: str, data: dict, headers: dict) -> dict:
    """Send a POST request and check the response for errors."""
    response = requests.post(url, data=json.dumps(data), headers=headers)
    response_status(response)
    response_json = json.loads(response.text)
    logging.info(f"Created: {response_json['html_url']}")
    return response_json


def main():
    parser = clparser()
    args = parser.parse_args()
    repo_name = args.repo_name
    auth_file = args.auth_file
    username = args.username
    token = args.token
    description = args.description
    public = args.public
    review = args.review
    base_url = "https://api.github.com"
    if auth_file:
        username, token = parse_auth_file(auth_file)
    else:
        if not username and not token:
            raise Exception(
                "No username or token supplied. View the help for more information.",
            )
    response = create_new_repo(
        base_url + "/user/repos",
        {
            "name": repo_name,
            "private": False if public else True,
            "description": description,
        },
        {"Authorization": "token {}".format(token)},
    )
    if review:
        review_changes(base_url, repo_name, username, token, response)


if __name__ == "__main__":
    main()
