import time
from typing import Tuple
from .parse import extract_form_values
from .exceptions import GenericError

# Logs in to the My SmartUTIL service.
# Must already have a valid session with the main City of Saskatoon portal
def smart_util_login(session) -> None:
    form_build_id, form_token, form_id = _get_login_form_details(session)
    _submit_login_form(session, form_build_id, form_token, form_id)
    _initialize(session)

def _get_login_form_details(session) -> Tuple[str, str, str]:
    resp = session.get('https://www.saskatoon.ca/services-residents/power-water/my-utility-account/account-summary', allow_redirects=False)
    if resp.status_code != 200:
        raise GenericError('Error getting login form details')
    return extract_form_values(str(resp.content))

def _submit_login_form(session, form_build_id: str, form_token: str, form_id: str) -> None:
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    resp = session.post('https://www.saskatoon.ca/services-residents/power-water/my-utility-account/account-summary', data={
        'op': 'My+SmartUTIL',
        'form_build_id': form_build_id,
        'form_token': form_token,
        'form_id': form_id
    }, headers=headers, allow_redirects=True)
    if resp.status_code != 200 or resp.url != 'https://smartutil.saskatoon.ca/HomeConnect/main.jsp':
        raise GenericError('Error logging into My SmartUTIL')

def _initialize(session):
    while True:
        resp = session.get('https://smartutil.saskatoon.ca/HomeConnect/Controller/InitializationStatus')
        if resp.status_code != 200:
            raise GenericError(f'Error initializing: {str(resp.content)}')
        jr = resp.json()
        if jr['initializationComplete']:
            return
        else:
            time.sleep(1)