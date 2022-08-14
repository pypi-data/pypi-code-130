import logging

from composition import directory
from composition.models import Action


def uninstall_application(application_id, template_location, app_details):
    logging.info(f"Uninstalling {application_id}")
    directory.handle_action(Action.DELETE, application_id=application_id)
