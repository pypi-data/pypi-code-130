import logging
import os
import sys
from os.path import exists
from pathlib import Path

from composition import install, uninstall, list_apps
from composition.models import Action, Application, generate_name
from composition.storage import get_yaml


def get_app_details(template):
    if not os.path.exists(os.path.join(os.getcwd(), template)):
        logging.error(f"Template file '{template}' not found in this directory.")
        sys.exit(1)
    app_yaml_path = os.path.join(os.getcwd(), "app.yaml")
    if not os.path.exists(app_yaml_path):
        logging.error(f"app.yaml not found in this directory.")
        sys.exit(1)
    app_details = get_yaml(app_yaml_path)
    if app_details is None:
        logging.error(f"Invalid app.yaml file at location {app_yaml_path}.")
        sys.exit(1)
    if "name" not in app_details or "version" not in app_details:
        logging.error(f"Invalid app.yaml at {app_yaml_path}.")
        logging.error("Must have a name and version.")
        return
    return app_details


def handle_action(action: Action, template="template.yaml", values=None, application_id=None):
    if values is None:
        values = ["values.yaml"]
    if application_id is None:
        application_id = generate_name()
    logging.info(f"Values: {values}")
    # First find all directories with app.yamls
    found_paths = find_file_paths('app.yaml')
    # Ensure there is at least a app.yaml and template in this directory
    app_details = get_app_details(template)
    app_name = app_details["name"]
    version = app_details["version"]
    # Handle any subdirectories and docker-compose ups
    for p in found_paths:
        handle_directory(template, p, action, application_id, values)
    # Create the application (it automatically registers itself)
    app = Application(os.getcwd(), app_name, version, application_id)
    logging.info(f"Successfully created installed {app.id}")
    logging.info("To view installed applications use `composer list`")
    # TODO remove
    list_apps.list_applications()


def find_file_paths(target_regex):
    found_paths = []
    for path in Path(os.getcwd()).rglob(target_regex):
        found_paths.append(path)
    return found_paths


def handle_directory(template, p: Path, action: Action, application_id, values):
    # Get the app details
    app_details = get_yaml(p)
    if app_details is None:
        logging.error(f"Invalid app.yaml file at location {p}, skipping.")
        return
    logging.debug(f"App details: {app_details}")
    directory = os.path.dirname(p)
    logging.debug(f"Handling Path: {directory}")
    # Check if the template.yaml is in the current directory
    template_location = os.path.join(directory, template)
    if not exists(template_location):
        logging.error(f"Could not find file {template_location}, skipping.")
        return
    logging.debug(f"Found {template_location} performing action {action.name}.")
    # Perform the desired action
    if action == Action.INSTALL:
        install.generate_template(directory, template, app_details, application_id, values)
    else:
        uninstall.uninstall_application(application_id, template_location, app_details)
