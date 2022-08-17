from click import prompt

from cchdo.auth import write_apikey


def do_bootstrap():
    """Interactivly set up the config file

    This command will create (or recreate) the config file used by the uow
    program. It will ask for one peice of information:

    1. Your api key (find this at https://cchdo.ucsd.edu/staff/me)

    It will create any intermediate directories as needed.
    """
    api_key = prompt("Your API Key")
    print("Writing apikey")
    write_apikey(api_key)
