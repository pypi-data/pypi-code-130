#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""standard python imports"""

from datetime import datetime

import click
from requests import exceptions
from rich.console import Console
from rich.progress import track

from app.api import Api
from app.application import Application
from app.logz import create_logger

logger = create_logger()


@click.group()
def cisa():
    """Update CISA"""


@cisa.command()
def update_kev():
    """Update RegScale Threats with latest KEV data."""
    data = update_known_vulnerabilities()
    update_regscale(data)


def update_alerts():
    """Update RegScale Threats with latest CISA Alerts."""


def update_known_vulnerabilities() -> dict:
    """Pull latest KEV data."""
    app = Application()
    api = Api(app)
    config = app.config
    api = Api(app)
    if "cisa_kev" in config:
        cisa_url = config["cisa_kev"]
    else:
        cisa_url = (
            "https://www.cisa.gov/sites/default/files/feeds/"
            "known_exploited_vulnerabilities.json"
        )
        config["cisa_kev"] = cisa_url
        app.save_config(config)
    response = api.get(url=cisa_url, headers={})
    try:
        response.raise_for_status()
    except exceptions.RequestException as ex:
        # Whoops it wasn't a 200
        logger.error("Error retrieving CISA KEV data: %s", str(ex))
    # Must have been a 200 status code
    json_obj = response.json()
    return json_obj


def convert_date_string(date_str: str):
    """_summary_

    Args:
        date_str (str): _description_

    Returns:
        _type_: _description_
    """
    fmt = "%Y-%m-%d"
    result_dt = datetime.strptime(
        date_str, fmt
    )  # 2022-11-03 to 2022-08-23T03:00:39.925Z
    return result_dt.isoformat() + ".000Z"


def regscale_threats(api: Api, config: dict) -> dict:
    """Return all regscale threats"""
    response = api.get(url=f"{config['domain']}/api/threats/getAll")
    return response.json()


def update_regscale(data: dict):
    """Update RegScale Threats with latest KEV data.

    Args:
        data (dict): Threat data
    """
    app = Application()
    config = app.config
    api = Api(app)
    console = Console()
    headers = {"Accept": "application/json", "Authorization": config["token"]}
    reg_threats = regscale_threats(api, config)
    unique_threats = list(set([reg["title"] for reg in reg_threats]))
    matching_threats = [
        d for d in data["vulnerabilities"] if d["vulnerabilityName"] in unique_threats
    ]
    url_threats = config["domain"] + "/api/threats"
    # reg_threats = api.get(url_threats).json()
    threats_loaded = []
    threats_updated = []
    new_threats = [
        dat for dat in data["vulnerabilities"] if dat not in matching_threats
    ]
    console.print(f"Found {len(new_threats)} new threats from CISA")
    if len([dat for dat in data["vulnerabilities"] if dat not in matching_threats]) > 0:
        for rec in track(
            new_threats,
            f"Posting {len(new_threats)} new threats to RegScale..",
        ):
            vuln = {
                "uuid": "",
                "title": rec["vulnerabilityName"],
                "threatType": "Specific",
                "threatOwnerId": config[
                    "userId"
                ],  # Application.get_user_name(app, api),
                "dateIdentified": convert_date_string(rec["dateAdded"]),
                # "dateResolved": convert_date_string(rec["dueDate"]),
                "targetType": "Other",
                "source": "Open Source",
                "description": rec["shortDescription"],
                "vulnerabilityAnalysis": rec["shortDescription"],
                "mitigations": rec["requiredAction"],
                "notes": rec["notes"].strip(),
                "dateCreated": convert_date_string(rec["dateAdded"]),
                "status": "Under Investigation",  # Post default to this, else don't update
            }
            # id = reg_threats[0]
            # do a dict search to pull id if available.
            response = api.post(url=url_threats, headers=headers, json=vuln)
            if not response.raise_for_status():
                threats_loaded.append(vuln)
    update_threats = [dat for dat in data["vulnerabilities"] if dat in matching_threats]
    if len(matching_threats) > 0:
        for rec in track(
            update_threats,
            f"Updating {len(update_threats)} existing threats in RegScale..",
        ):
            update_vuln = {
                "uuid": "",
                "title": rec["vulnerabilityName"],
                "dateIdentified": convert_date_string(rec["dateAdded"]),
                # "dateResolved": convert_date_string(rec["dueDate"]),
                "source": "Open Source",
                "description": rec["shortDescription"],
                "vulnerabilityAnalysis": rec["shortDescription"],
                "dateCreated": convert_date_string(rec["dateAdded"]),
            }
            old_vuln = [
                threat
                for threat in reg_threats
                if threat["title"] == update_vuln["title"]
            ][0]
            update_vuln["status"] = old_vuln["status"]
            update_vuln["threatType"] = old_vuln["threatType"]
            update_vuln["threatOwnerId"] = old_vuln["threatOwnerId"]
            update_vuln["status"] = old_vuln["status"]
            update_vuln["mitigations"] = old_vuln["mitigations"]
            update_vuln["targetType"] = old_vuln["targetType"]
            # id = reg_threats[0]
            # do a dict search to pull id if available.
            if old_vuln:
                put_res = api.put(url=url_threats, headers=headers, json=update_vuln)
                if not put_res.raise_for_status():
                    threats_updated.append(update_vuln)
    # Update Matching Threats
    logger.debug(threats_loaded)
    logger.debug(threats_updated)
    if len(threats_loaded) > 0:
        console.print("Loaded {:,} new threats to RegScale".format(len(threats_loaded)))
    console.print(
        "Updated {:,} existing threats in RegScale".format(len(threats_updated))
    )
