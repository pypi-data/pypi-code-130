# Copyright 2022 Karlsruhe Institute of Technology
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# pylint: disable=missing-function-docstring
import requests
from flask import Blueprint
from flask import current_app
from flask import render_template
from flask import request
from flask_login import login_required

from . import DEFAULT_CONTENT_TYPE
from . import PLUGIN_NAME
from . import USER_CONFIG_INFLUXDBS
from .utils import InfluxDBConfigForm
from kadi.lib.web import qparam
from kadi.plugins import api_bp
from kadi.plugins import const
from kadi.plugins import get_plugin_config
from kadi.plugins import get_user_config
from kadi.plugins import hookimpl
from kadi.plugins import json_error_response
from kadi.plugins import json_response
from kadi.plugins import url_for


bp = Blueprint(
    PLUGIN_NAME,
    __name__,
    url_prefix="/influxdb",
    template_folder="templates",
    static_folder="static",
)


@hookimpl
def kadi_register_blueprints(app):
    app.register_blueprint(bp)


@hookimpl
def kadi_register_capabilities():
    return "influxdb"


@hookimpl
def kadi_get_scripts():
    if request.endpoint != "settings.manage_preferences":
        return None

    return url_for("influxdb.static", filename="influxdb-field.js")


@hookimpl
def kadi_get_translations_bundles(locale):
    translations = {
        "de": {
            "Database disabled.": "Datenbank deaktiviert.",
            "Name": "Name",
            "Token": "Token",
        }
    }
    return translations.get(locale)


def _validate_instance_config(plugin_config, name):
    instance_config = plugin_config.get(name)

    if not isinstance(instance_config, dict) or not instance_config.get("url"):
        current_app.logger.error(
            f"Invalid configuration for '{name}' in '{PLUGIN_NAME}' plugin."
        )
        return False

    return True


@api_bp.post("/influxdb/<name>/query")
@login_required
@qparam("orgID")
def influxdb_query(name, qparams):
    """Query data from a configured InfluxDB instance.

    This endpoint is simply a proxy to the InfluxDB query endpoint documented at:
    https://docs.influxdata.com/influxdb/v2.2/api/#operation/PostQuery
    """
    plugin_config = get_plugin_config(PLUGIN_NAME)

    if not _validate_instance_config(plugin_config, name):
        return json_error_response(500, f"InfluxDB '{name}' is configured incorrectly.")

    user_config = get_user_config(key=USER_CONFIG_INFLUXDBS, default=[], decrypt=True)
    user_config = {config["name"]: config for config in user_config}

    if name not in user_config or not user_config[name]["token"]:
        return json_error_response(
            401, f"No access token was supplied for InfluxDB '{name}'."
        )

    # Set the headers required by InfluxDB.
    content_type = request.content_type

    if content_type not in [DEFAULT_CONTENT_TYPE, const.MIMETYPE_JSON]:
        content_type = DEFAULT_CONTENT_TYPE

    headers = {
        "Authorization": f"Token {user_config[name]['token']}",
        "Content-Type": content_type,
    }

    try:
        url = f"{plugin_config[name]['url']}/api/v2/query?orgID={qparams['orgID']}"
        response = requests.post(
            url=url,
            data=request.data,
            headers=headers,
            timeout=plugin_config[name].get("timeout", 10),
        )

    except requests.ConnectionError:
        return json_error_response(
            502,
            description=f"Failed to establish a connection to InfluxDB '{name}'.",
        )

    except requests.Timeout:
        return json_error_response(
            504,
            description="Timeout while trying to establish a connection to InfluxDB"
            f" '{name}'.",
        )

    except Exception as e:
        current_app.logger.exception(e)
        return json_error_response(
            500, description=f"Request to InfluxDB '{name}' failed."
        )

    # Return errors that are produced directly by the accessed InfluxDB instance as-is.
    if response.status_code != 200:
        return json_response(response.status_code, body=response.json())

    return current_app.response_class(response.content, mimetype=const.MIMETYPE_CSV)


@hookimpl
def kadi_get_preferences_config():
    plugin_config = get_plugin_config(PLUGIN_NAME)
    influxdbs = {}

    for name in plugin_config:
        if _validate_instance_config(plugin_config, name):
            influxdbs[name] = {
                "title": plugin_config[name].get("title", name),
                "query_endpoint": url_for("api.influxdb_query", name=name, orgID="..."),
            }

    user_config = get_user_config(key=USER_CONFIG_INFLUXDBS, decrypt=True)

    # Check if either at least one valid InfluxDB instance is configured or if the
    # current user configured any InfluxDB instance in the past.
    if not influxdbs and not user_config:
        return None

    form = InfluxDBConfigForm()

    return {
        "title": "InfluxDB",
        "form": form,
        "get_template": lambda: render_template(
            "influxdb/preferences.html", form=form, influxdbs=influxdbs
        ),
    }
