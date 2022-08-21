import logging
import typing

from flask import Request

from .formresponse import FormResponse


class Event:
    event_id: str
    event_type: str
    form_response: FormResponse

    def __init__(self, event_id: str, event_type: str,
                 form_response: FormResponse):
        self.event_id = event_id
        self.event_type = event_type
        self.form_response = form_response

    def __str__(self):
        return f'Event {self.event_id} ({self.event_type}): \n {self.form_response}'

    def __repr__(self):
        return self.__str__()

    @classmethod
    def from_request(cls, request: Request, shared_secret: typing.Optional[str] = None):
        if shared_secret is not None:
            # Need to verify this is a valid response using data from the headers
            if not Event._verify_event_with_shared_secret(request=request, shared_secret=shared_secret):
                event_id = request.get_json().get('event_id', None)
                raise ConnectionError(f"Could not verify incoming request with event_id {event_id}")

        return cls.from_event_json(event_json=request.get_json())

    @classmethod
    def from_event_json(cls, event_json: dict):
        event_id = event_json.get('event_id', None)
        event_type = event_json.get('event_type', None)
        form_response_json = event_json.get('form_response', None)
        form_response = FormResponse.from_form_response_json(form_response_json)

        return cls(event_id=event_id, event_type=event_type, form_response=form_response)

    @staticmethod
    def _verify_event_with_shared_secret(request: Request, shared_secret: str) -> bool:
        import hmac
        import base64
        from hashlib import sha256
        payload = request.get_data()
        event_id = request.get_json().get('event_id', None)

        # Verify that the HMAC hash matches the body data
        provided_signature = request.headers.get('typeform-signature')
        digest = hmac.new(shared_secret.encode('utf-8'), payload, sha256).digest()
        calculated_signature = f"sha256={base64.b64encode(digest).decode()}"
        logging.debug(f"Calculated signature {calculated_signature} for event_id {event_id}")

        if calculated_signature == provided_signature:
            logging.info(f'Verified shared secret on incoming request; '
                         f'request with event_id {event_id} is legitimate.')
            return True
        else:
            logging.info(f'Could not verify shared secret on incoming request; '
                         f'request with event_id {event_id} may not be legitimate. '
                         f'Calculated signature: {calculated_signature}, but received signature {provided_signature}')
            return False
