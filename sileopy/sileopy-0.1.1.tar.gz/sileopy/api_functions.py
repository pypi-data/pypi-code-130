# -*- coding: utf-8 -*-
"""
This module contains methods for connecting to API endpoints using the
requests module.
"""
# Python module imports
import logging

# 3rd party module imports
import requests

# Local module imports
from sileopy.common_functions import tracelog


# Logger setup
logger = logging.getLogger(__name__)


@tracelog
def get_request(entity_name, url, api_token):
    """
    Fetch data from API endpoint with a HTTP GET request

    Parameters
    ----------
    entity_name : str
        Name of entity to be fetched from API endpoint
    url : str
        API endpoint URL
    api_token: str
        Token for api-authentication

    Returns
    -------
    Dictionary with the JSON response from the request
    """
    try:
        headers = {'Authorization': api_token}

        http_request = requests.get(
            url,
            headers=headers
        )

        if http_request.status_code == 200:
            logger.info("GET of %s successful.", entity_name)
        else:
            logger.error(
                "GET of %s failed. Error %s",
                entity_name,
                http_request.status_code
            )
            raise requests.ConnectionError("Unexpected HTTP status code.")

        return http_request.json()
    except requests.ConnectionError as connection_error:
        logger.error(
            "Connection error when GETting data from API-endpoint: %s",
            connection_error
        )
        raise connection_error


@tracelog
def post_request(entity_name, url, post_data, api_token):
    """
    Send data to PRIO using a HTTP POST request

    Parameters
    ----------
    entity_name : str
        Name of entity to be fetched from PRIO
    url : str
        API endpoint URL
    post_data : dict
        Dictionary containing data fields to POST in JSON format
    api_token: str
        Token for api-authentication

    Returns
    -------
    Dictionary with the JSON response from the request
    """
    try:
        headers = {'Authorization': api_token}

        http_request = requests.post(
            url,
            data=post_data,
            headers=headers
        )

        if http_request.status_code in (200, 201):
            logger.info("POST of %s successful.", entity_name)
        else:
            logger.error(
                "POST of %s failed. Error: %s",
                entity_name,
                http_request.status_code
            )
            raise requests.ConnectionError("Unexpected HTTP status code.")

        return http_request.json()
    except requests.ConnectionError as connection_error:
        logger.error(
            "Connection error when POSTing data to API-endpoint: %s",
            connection_error
        )
        raise connection_error


@tracelog
def patch_request(entity_name, url, post_data, api_token):
    """
    Send data to PRIO using a HTTP PATCH request

    Parameters
    ----------
    entity_name : str
        Name of entity to be fetched from PRIO
    url : str
        API endpoint URL
    post_data : dict
        Dictionary containing data fields to PATCH in JSON format
    api_token: str
        Token for api-authentication

    Returns
    -------
    Dictionary with the JSON response from the request
    """
    try:
        headers = {'Authorization': api_token}

        http_request = requests.patch(
            url,
            data=post_data,
            headers=headers
        )

        if http_request.status_code in (200, 201):
            logger.info("PATCH of %s successful.", entity_name)
        else:
            logger.error(
                "PATCH of %s failed. Error: %s",
                entity_name,
                http_request.status_code
            )
            raise requests.ConnectionError("Unexpected HTTP status code.")

        return http_request.json()
    except requests.ConnectionError as connection_error:
        logger.error(
            "Connection error when PATCHing data to API-endpoint: %s",
            connection_error
        )
        raise connection_error


@tracelog
def get_prio_version(url, api_token):
    """
    Get current version number of PRIO

    Parameters
    ----------
    url : str
        API endpoint URL
    api_token: str
        Token for api-authentication

    Returns
    -------
    String with the current PRIO version
    """
    try:
        version_data = get_request(
            'prio version'
            , url + 'version/'
            , api_token
        )

        prio_version = version_data['version']

        logger.info("PRIO API Version: %s", prio_version)

        return prio_version

    except requests.ConnectionError as connection_error:
        logger.error("Connection failed: %s", connection_error)


@tracelog
def verify_prio_version(url, api_token, prio_version):
    """
    Check if the current version number of PRIO matches the supported version
    at the caller

    Parameters
    ----------
    url : str
        API endpoint URL
    api_token: str
        Token for api-authentication
    prio_version: str
        Prio version to check

    Returns
    -------
    True if the version number of PRIO matches supported version
    """

    current_prio_version = get_prio_version(url, api_token)

    if current_prio_version == prio_version:
        return True

    return False
