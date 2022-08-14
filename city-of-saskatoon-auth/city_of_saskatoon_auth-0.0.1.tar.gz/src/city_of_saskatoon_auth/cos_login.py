from .parse import *
from .exceptions import GenericError, InvalidCredentials

# Logs in to the main City of Saskatoon portal
# Checks if we already have valid auth before trying to log in
def cos_login(session) -> None:
    if check_cos_login(session):
        return
    login_form_url = _get_login_form_url(session)
    saml_response = _post_login_form_and_get_saml_response(session, login_form_url)
    _submit_saml_response(session, saml_response)
    _finalize(session)

# Checks if the current session is valid for the City of Saskatoon portal
def check_cos_login(session) -> bool:
    resp = session.get(f'https://www.saskatoon.ca/users/{session.username}', allow_redirects=False)
    if resp.status_code == 200:
        return True
    return False

def _get_login_form_url(session) -> str:
    resp = session.get('https://www.saskatoon.ca/saml_login/', allow_redirects=False)
    if resp.status_code != 302:
        raise GenericError(f'Got status {resp.status_code} when attemtpting to retrieve login form URL')
    login_url = resp.headers['Location']
    if not login_url:
        raise GenericError('Error getting login url')
    return login_url

def _post_login_form_and_get_saml_response(session, login_url: str) -> str:
    resp = session.post(login_url, data={
        'UserName': f'public\{session.username}',
        'Password': session.password,
        'AuthMethod': 'FormsAuthentication'
    }, allow_redirects=True)
    saml_response = extract_saml_response(str(resp.content))
    if not saml_response:
        raise InvalidCredentials
    return saml_response

def _submit_saml_response(session, saml_response: str) -> None:
    resp = session.post('https://www.saskatoon.ca/simplesaml/module.php/saml/sp/saml2-acs.php/default-sp', data = {
        'SAMLResponse': saml_response,
        'RelayState': 'https://www.saskatoon.ca/saml_login'
    })
    if resp.status_code != 200:
        raise GenericError('Invalid response from simplesaml')

def _finalize(session) -> None:
    resp = session.get('https://www.saskatoon.ca/saml_login/', allow_redirects=True)
    if resp.status_code != 200:
        GenericError('Invalid response from saml_login')
