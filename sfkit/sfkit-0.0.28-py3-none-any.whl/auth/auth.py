import json
import os

from google.auth.transport import requests as google_requests
from sfkit.protocol.utils import constants
from sfkit.utils import get_study_options_for_sa_email


def auth(sa_key_file: str, study_title: str) -> None:
    """
    Authenticate a GCP service account from the study with the sfkit CLI.
    """

    # TODO: add service account jwt to get requests instead
    if not sa_key_file:
        sa_key_file = input("Enter absolute path to service account private key file: ")
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = sa_key_file

    with open(sa_key_file, "r") as f:
        data = json.load(f)
        sa_email = data["client_email"]

    # confirm that the service account private key file is valid
    try:
        google_requests.Request()  # basic check to make sure the key is valid
    except Exception as e:
        print(f"Error: {e}")
        print("Please make sure the service account private key file is valid.")
        exit(1)

    if study_title:
        user_email = "Broad"
    else:
        # get email and study title for this service account from the database
        study_title, user_email = "", ""

        options = get_study_options_for_sa_email(sa_email)
        if not options:
            print("Error finding your study.  Please make sure you service account key corresponds to a valid study.")
            exit(1)
        if len(options) == 1:
            study_title, user_email = options[0]
        else:
            print("Please select your study:")
            for i, option in enumerate(options):
                print(f"{i}: {option[0]}")
            study_title, user_email = options[int(input("Enter your selection: "))]

    # if path to constants.AUTH_FILE does not exist, create it
    os.makedirs(constants.SFKIT_DIR, exist_ok=True)
    with open(constants.AUTH_FILE, "w") as f:
        f.write(user_email + "\n")
        f.write(study_title + "\n")
        f.write(f"{sa_key_file}\n")

    print("Successfully authenticated!")
