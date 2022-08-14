import re
from typing import Tuple

def extract_saml_response(body: str) -> str:
    return _extract_first_group(body, r"name=\"SAMLResponse\" value=\"(.*?)\"")

def extract_form_values(body: str) -> Tuple[str, str, str]:
    form_build_id = _extract_first_group(body, r"name=\"form_build_id\" value=\"(.*?)\"")
    form_token = _extract_first_group(body, r"name=\"form_token\" value=\"(.*?)\"")
    form_id = _extract_first_group(body, r"name=\"form_id\" value=\"(.*?)\"")
    return (form_build_id, form_token, form_id)

def _extract_first_group(content: str, regex: str) -> str:
    p = re.compile(regex)
    m = p.search(content)
    return m.group(1)