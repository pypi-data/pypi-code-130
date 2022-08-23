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
from flask import abort
from flask import redirect
from flask import render_template
from flask import request
from flask_babel import gettext as _
from flask_login import current_user
from flask_login import login_required

import kadi.lib.constants as const
from .blueprint import bp
from .core import create_collection
from .core import delete_collection as _delete_collection
from .core import link_collections
from .core import update_collection
from .forms import AddCollectionPermissionsForm
from .forms import AddRecordsPermissionsForm
from .forms import EditCollectionForm
from .forms import LinkCollectionsForm
from .forms import LinkRecordsForm
from .forms import NewCollectionForm
from .models import Collection
from .models import CollectionState
from .utils import get_child_collections
from .utils import get_parent_collections
from kadi.ext.db import db
from kadi.lib.exceptions import KadiPermissionError
from kadi.lib.permissions.core import get_permitted_objects
from kadi.lib.permissions.core import has_permission
from kadi.lib.permissions.utils import permission_required
from kadi.lib.publication import get_publication_provider
from kadi.lib.publication import get_publication_providers
from kadi.lib.resources.tasks import start_publish_resource_task
from kadi.lib.resources.views import add_links
from kadi.lib.resources.views import add_roles
from kadi.lib.resources.views import copy_roles
from kadi.lib.resources.views import remove_roles
from kadi.lib.web import danger
from kadi.lib.web import info
from kadi.lib.web import qparam
from kadi.lib.web import success
from kadi.lib.web import url_for
from kadi.modules.accounts.models import User
from kadi.modules.groups.models import Group
from kadi.modules.records.models import Record
from kadi.modules.records.models import RecordState


@bp.get("")
@login_required
@qparam("user", multiple=True, parse=int)
def collections(qparams):
    """Collection overview page.

    Allows users to search and filter for collections or create new ones.
    """
    users = []

    if qparams["user"]:
        users = User.query.filter(User.id.in_(qparams["user"]))

    return render_template(
        "collections/collections.html",
        title=_("Collections"),
        js_resources={"users": [(u.id, f"@{u.identity.username}") for u in users]},
    )


@bp.route("/new", methods=["GET", "POST"])
@permission_required("create", "collection", None)
@qparam("collection", default=None, parse=int)
def new_collection(qparams):
    """Page to create a new collection."""
    copied_collection = None

    # Copy a collection's metadata.
    if request.method == "GET" and qparams["collection"] is not None:
        copied_collection = Collection.query.get_active(qparams["collection"])

        if copied_collection is not None and not has_permission(
            current_user, "read", "collection", copied_collection.id
        ):
            copied_collection = None

    form = NewCollectionForm(collection=copied_collection)

    if request.method == "POST":
        if form.validate():
            collection = create_collection(
                identifier=form.identifier.data,
                title=form.title.data,
                description=form.description.data,
                visibility=form.visibility.data,
                tags=form.tags.data,
            )

            if collection:
                add_links(collection.records, Record, form.linked_records.data)
                copy_roles(collection, form.copy_permission.data)
                db.session.commit()

                success(_("Collection created successfully."))
                return redirect(
                    url_for("collections.view_collection", id=collection.id)
                )

        danger(_("Error creating collection."))

    return render_template(
        "collections/new_collection.html",
        title=_("New collection"),
        form=form,
        js_resources={"title_field": form.title.to_dict()},
    )


@bp.route("/<int:id>/edit", methods=["GET", "POST"])
@permission_required("update", "collection", "id")
def edit_collection(id):
    """Page to edit an existing collection."""
    collection = Collection.query.get_active_or_404(id)
    form = EditCollectionForm(collection)

    if request.method == "POST":
        if form.validate():
            if update_collection(
                collection,
                title=form.title.data,
                identifier=form.identifier.data,
                description=form.description.data,
                visibility=form.visibility.data,
                tags=form.tags.data,
            ):
                success(_("Changes saved successfully."))

                if form.submit_quit.data:
                    return redirect(
                        url_for("collections.view_collection", id=collection.id)
                    )

                return redirect(
                    url_for("collections.edit_collection", id=collection.id)
                )

        danger(_("Error editing collection."))

    return render_template(
        "collections/edit_collection.html",
        title=_("Edit collection"),
        form=form,
        collection=collection,
        js_resources={"title_field": form.title.to_dict()},
    )


@bp.get("/<int:id>")
@permission_required("read", "collection", "id")
def view_collection(id):
    """Page to view a collection."""
    collection = Collection.query.get_active_or_404(id)
    return render_template(
        "collections/view_collection.html",
        collection=collection,
        publication_providers=get_publication_providers(collection),
        parents=get_parent_collections(collection),
        has_children=len(get_child_collections(collection)) > 0,
        js_resources={
            "get_records_endpoint": url_for(
                "api.get_collection_records", id=collection.id
            ),
            "search_records_endpoint": url_for(
                "records.records", collection=collection.id
            ),
        },
    )


@bp.get("/<int:id>/export/<export_type>")
@permission_required("read", "collection", "id")
def export_collection(id, export_type):
    """Page to view the exported data of a collection.

    Currently ``"json"`` and ``"qr"`` are supported as export type.
    """
    collection = Collection.query.get_active_or_404(id)
    export_types = const.EXPORT_TYPES["collection"]

    if export_type not in export_types:
        abort(404)

    return render_template(
        "collections/export_collection.html",
        title=export_types[export_type],
        collection=collection,
        export_type=export_type,
    )


@bp.route("/<int:id>/publish/<provider>", methods=["GET", "POST"])
@permission_required("read", "collection", "id")
def publish_collection(id, provider):
    """Page to publish a collection using a given provider."""
    collection = Collection.query.get_active_or_404(id)
    publication_provider = get_publication_provider(provider, collection)

    if publication_provider is None:
        abort(404)

    if request.method == "POST":
        endpoint = url_for(
            "collections.publish_collection", id=collection.id, provider=provider
        )

        if not publication_provider["is_connected"]:
            return redirect(endpoint)

        status, task = start_publish_resource_task(
            provider, collection, dict(request.form)
        )

        if not status:
            info(_("A publishing task is already in progress."))
        elif not task:
            danger(_("Error starting publishing task."))
        else:
            success(_("Publishing task started successfully."))

        return redirect(endpoint)

    return render_template(
        "collections/publish_collection.html",
        title=publication_provider["title"],
        collection=collection,
        provider=publication_provider,
    )


@bp.route("/<int:id>/links", methods=["GET", "POST"])
@permission_required("link", "collection", "id")
@qparam("tab", default="records")
def manage_links(id, qparams):
    """Page to link a collection to records or other collections."""
    collection = Collection.query.get_active_or_404(id)

    records_form = LinkRecordsForm(suffix="records")
    collections_form = LinkCollectionsForm(suffix="collections")

    if qparams["tab"] == "records" and records_form.validate_on_submit():
        add_links(collection.records, Record, records_form.records.data)
        db.session.commit()

        success(_("Changes saved successfully."))

    elif qparams["tab"] == "collections" and collections_form.validate_on_submit():
        collections_query = Collection.query.filter(
            Collection.id.in_(collections_form.collections.data),
            Collection.state == CollectionState.ACTIVE,
        )

        for child_collection in collections_query:
            try:
                link_collections(collection, child_collection)
            except KadiPermissionError:
                pass

        db.session.commit()
        success(_("Changes saved successfully."))

    return render_template(
        "collections/manage_links.html",
        title=_("Manage links"),
        records_form=records_form,
        collections_form=collections_form,
        collection=collection,
    )


@bp.route("/<int:id>/permissions", methods=["GET", "POST"])
@permission_required("permissions", "collection", "id")
@qparam("tab", default="collection")
def manage_permissions(id, qparams):
    """Page to manage access permissions of a collection."""
    collection = Collection.query.get_active_or_404(id)

    collection_form = AddCollectionPermissionsForm(suffix="collection")
    records_form = AddRecordsPermissionsForm(suffix="records")

    if qparams["tab"] == "collection" and collection_form.validate_on_submit():
        add_roles(
            User, collection_form.users.data, collection, collection_form.role.data
        )
        add_roles(
            Group, collection_form.groups.data, collection, collection_form.role.data
        )
        db.session.commit()

        success(_("Changes saved successfully."))
        return redirect(url_for("collections.manage_permissions", id=collection.id))

    if qparams["tab"] == "records" and records_form.validate_on_submit():
        record_ids_query = (
            get_permitted_objects(current_user, "permissions", "record")
            .filter(Record.state == RecordState.ACTIVE)
            .with_entities(Record.id)
        )
        records = collection.records.filter(Record.id.in_(record_ids_query))

        for record in records:
            # Always remove the roles first, which easily allows changing existing roles
            # as well.
            remove_roles(User, records_form.users.data, record)
            remove_roles(Group, records_form.groups.data, record)

            if records_form.role.data:
                add_roles(User, records_form.users.data, record, records_form.role.data)
                add_roles(
                    Group, records_form.groups.data, record, records_form.role.data
                )

        db.session.commit()

        success(_("Changes saved successfully."))
        return redirect(
            url_for("collections.manage_permissions", id=collection.id, tab="records")
        )

    return render_template(
        "collections/manage_permissions.html",
        title=_("Manage permissions"),
        collection_form=collection_form,
        records_form=records_form,
        collection=collection,
    )


@bp.get("/<int:collection_id>/revisions/<int:revision_id>")
@permission_required("read", "collection", "collection_id")
def view_revision(collection_id, revision_id):
    """Page to view a specific revision of a collection."""
    collection = Collection.query.get_active_or_404(collection_id)
    revision = collection.revisions.filter(
        Collection.revision_class.id == revision_id
    ).first_or_404()

    return render_template(
        "collections/view_revision.html",
        title=_("Revision"),
        collection=collection,
        revision=revision,
    )


@bp.post("/<int:id>/delete")
@permission_required("delete", "collection", "id")
def delete_collection(id):
    """Endpoint to delete an existing collection.

    Does basically the same as the corresponding API endpoint.
    """
    collection = Collection.query.get_active_or_404(id)
    _delete_collection(collection)

    success(_("Collection deleted successfully."))
    return redirect(url_for("collections.collections"))
