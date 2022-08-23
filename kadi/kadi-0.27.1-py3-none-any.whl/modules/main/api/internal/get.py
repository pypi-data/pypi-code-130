# Copyright 2020 Karlsruhe Institute of Technology
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
from flask_login import current_user
from flask_login import login_required

import kadi.lib.constants as const
from kadi.ext.db import db
from kadi.lib.api.blueprint import bp
from kadi.lib.api.core import internal
from kadi.lib.api.core import json_response
from kadi.lib.conversion import normalize
from kadi.lib.conversion import strip
from kadi.lib.db import escape_like
from kadi.lib.permissions.core import get_permitted_objects
from kadi.lib.resources import RESOURCE_TYPES
from kadi.lib.resources.schemas import BasicResourceSchema
from kadi.lib.web import qparam
from kadi.modules.main.utils import get_licenses
from kadi.modules.main.utils import get_tags


@bp.get("/tags/select", v=None)
@login_required
@internal
@qparam("page", default=1, parse=int)
@qparam("term", parse=normalize)
@qparam("type", default=None)
def select_tags(qparams):
    """Search tags in dynamic selections.

    Similar to :func:`kadi.lib.resources.api.get_selected_resources`. Only the tags of
    resources the current user has read permission for are returned.
    """
    paginated_tags = get_tags(
        filter_term=qparams["term"], resource_type=qparams["type"]
    ).paginate(qparams["page"], 10, False)

    data = {
        "results": [],
        "pagination": {"more": paginated_tags.has_next},
    }
    for tag in paginated_tags.items:
        data["results"].append({"id": tag.name, "text": tag.name})

    return json_response(200, data)


@bp.get("/licenses/select", v=None)
@login_required
@internal
@qparam("page", default=1, parse=int)
@qparam("term", parse=strip)
def select_licenses(qparams):
    """Search licenses in dynamic selections.

    Similar to :func:`kadi.lib.resources.api.get_selected_resources`.
    """
    paginated_licenses = get_licenses(filter_term=qparams["term"]).paginate(
        qparams["page"], 10, False
    )

    data = {
        "results": [],
        "pagination": {"more": paginated_licenses.has_next},
    }
    for license in paginated_licenses.items:
        data["results"].append({"id": license.name, "text": license.title})

    return json_response(200, data)


@bp.get("/search", v=None)
@login_required
@internal
@qparam("query", parse=normalize)
def search_resources(qparams):
    """Search for different resources.

    Currently used in the base navigation quick search. Supports resources of type
    :class:`.Record`, :class:`.Collection`, :class:`.Template` and :class:`.Group`.
    """
    resource_queries = []

    for resource_type, resource_meta in RESOURCE_TYPES.items():
        model = resource_meta["model"]

        resources_query = (
            get_permitted_objects(current_user, "read", resource_type)
            .filter(
                model.state == const.MODEL_STATE_ACTIVE,
                model.identifier.ilike(f"%{escape_like(qparams['query'])}%"),
            )
            .with_entities(
                model.id,
                model.identifier,
                model.last_modified.label("last_modified"),
                db.literal(resource_type).label("type"),
                db.literal(str(resource_meta["title"])).label("pretty_type"),
            )
        )

        resource_queries.append(resources_query)

    resources = (
        resource_queries[0]
        .union(*resource_queries[1:])
        .order_by(db.desc("last_modified"))
        .limit(5)
    )

    return json_response(200, BasicResourceSchema(many=True).dump(resources))
