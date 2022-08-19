import logging

from composition import directory, api, storage


def uninstall_application(application_id, force):
    logging.info(f"Uninstalling {application_id}")
    directory.handle_delete(application_id, force=force)
    storage.remove(application_id)

