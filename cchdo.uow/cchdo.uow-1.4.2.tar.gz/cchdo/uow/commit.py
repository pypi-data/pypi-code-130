import click


from hashlib import sha256
import json
import os
from base64 import b64encode
from mimetypes import guess_type
from copy import deepcopy


from . import get_uow_info, get_fetch_events, API_ENDPOINT
from .uow_json import load_uow_json


blank_file_json = {
    "file": {"body": "", "type": "", "name": ""},
    "container_contents": [],
    "data_container": "",
    "data_format": "",
    "data_type": "",
    "file_hash": "",
    "file_name": "",
    "file_path": "",
    "file_size": 0,
    "file_sources": [],
    "file_type": "",
    "other_roles": [],
    "permissions": [],
    "role": "",
    "submissions": [],
    "events": [],
}


def _hash_key_events(filtered_events):
    hash_events = {}
    for event in filtered_events:
        file_hash = event["file_hash"]
        hash_events[file_hash] = event
    return hash_events


def _hash_file(path):
    file_hash = sha256()
    with open(path, "rb") as f:
        file_hash.update(f.read())
    return file_hash.hexdigest()


def _prepare_processing_note(uow_json, basedir):
    note = {
        "action": uow_json["processing_note"]["action"],
        "body": [uow_json["processing_note"]["notes"]],
        "data_type": uow_json["processing_note"]["data_type"],
        "date": uow_json["processing_note"]["date"],
        "name": uow_json["processing_note"]["name"],
        "summary": uow_json["processing_note"]["summary"],
    }
    if note["body"][0].startswith("@"):
        path = os.path.join(basedir, note["body"][0][1:])
        with open(path, "r") as f:
            note["body"] = f.read().splitlines()
    return note


def _prepare_api_calls(uow_json, events, for_human=False):
    config, basedir = get_uow_info()
    api_calls = []
    events = _hash_key_events(events)
    file_to_hash = {}

    warnings = []

    for file in uow_json["files"]:
        file_path = os.path.join(basedir, file["file"])
        file_to_hash[file["file"]] = _hash_file(file_path)

    for file in uow_json["files"]:
        file_path = os.path.join(basedir, file["file"])
        file_json = deepcopy(blank_file_json)
        file_hash = file_to_hash[file["file"]]

        file_json["file_hash"] = file_hash
        file_json["file_name"] = os.path.basename(file_path)
        file_json["file_type"] = guess_type(file_json["file_name"])[0]
        file_json["file"]["name"] = file_json["file_name"]
        file_json["file"]["type"] = file_json["file_type"]

        with open(file_path, "rb") as f:
            file_json["file"]["body"] = b64encode(f.read()).decode("utf8")

        event = {
            "name": uow_json["processing_note"]["name"],
            "notes": "",
            "date": uow_json["processing_note"]["date"] + "T00:00:00Z",
            "type": "merge",
        }

        if file["action"] == "merge":
            try:
                file_metadata = events[file_hash]
            except KeyError:
                print("file marked as merged not in fetch events")
                raise click.Abort()
            api_call = {
                "route": f"/file/{file_metadata['id']}",
                "method": "PATCH",
                "data": '[{"path":"/role","op":"replace","value":"merged"},{"path":"/events/0", "op":"add", "value":'
                + json.dumps(event)
                + "}]",
                "check": file_metadata["file_hash"],
            }
            if for_human:
                print(
                    f"({file_metadata['id']}) {file_metadata['file_name']} will be PATCHed as having been merged"
                )
                if len(file_metadata.get("__uow_crusie_list", [])) > 1:
                    warnings.append(
                        f"({file_metadata['id']}) {file_metadata['file_name']} is attached to more than one cruise"
                    )
            api_calls.append(api_call)

        elif file["action"] == "new" and "replaces" in file:
            replaces_hash = file_to_hash[file["replaces"]]

            replaces_format = events[replaces_hash]["data_format"]
            replaces_type = events[replaces_hash]["data_type"]
            replaces_role = events[replaces_hash]["role"]
            file_json["data_format"] = replaces_format
            file_json["data_type"] = replaces_type
            file_json["role"] = replaces_role

            if "from" in file:
                hashes = [file_to_hash[source] for source in file["from"]]
                file_json["file_sources"] = hashes

            api_call = {
                "route": "/file",
                "method": "POST",
                "data": json.dumps(file_json),
                "check": file_json["file_hash"],
            }
            api_calls.append(api_call)

            if for_human:
                print(
                    (
                        f"(new) {file['file']} will be POSTed to replace ({events[replaces_hash]['id']}) {events[replaces_hash]['file_name']}. "
                        f"It will have the role: {replaces_role}, data_type: {replaces_type}, data_format: {replaces_format}"
                    )
                )

        elif file["action"] == "new":
            new_role = file["role"]
            new_format = file["data_format"]
            new_type = file["data_type"]
            file_json["data_format"] = new_format
            file_json["data_type"] = new_type
            file_json["role"] = new_role

            if "from" in file:
                hashes = [file_to_hash[source] for source in file["from"]]
                file_json["file_sources"] = hashes

            api_call = {
                "route": "/file",
                "method": "POST",
                "data": json.dumps(file_json),
                "check": file_json["file_hash"],
            }
            api_calls.append(api_call)

            if for_human:
                print(
                    (
                        f"(new) {file['file']} will be POSTed. "
                        f"It will have the role: {new_role}, data_type: {new_type}, data_format: {new_format}"
                    )
                )
        else:
            print("The API Payload failed to be built..")
            raise click.Abort()

    note = _prepare_processing_note(uow_json, basedir)
    api_calls.append(
        {
            "route": f"/cruise/{config['cruise_id']}",
            "method": "PATCH",
            "data": json.dumps([{"path": "/notes/0", "op": "add", "value": note}]),
        }
    )
    if for_human:
        print(
            f"The following history note will be attached to the cruise: {json.dumps(note, indent=2)}"
        )

        if len(warnings) > 0:
            print("### WARNINGS ###")
            for warning in warnings:
                print(warning)

    return api_calls


def _check_api_calls_sanity(api_calls):
    """We want to make sure the all the POST calls are not going to
    conflict with an existing resource, we also want to ensure that the PATCH
    calls will modify a resource that both exists and the id route matches the
    hash we expect.

    This should greatly increase the chance of the commit success
    """
    from cchdo.auth.session import session

    file_list_url = f"{API_ENDPOINT}/file"
    r = session.get(file_list_url)
    if not r.status_code == 200:
        print("Something has gone wrong loading the cchdo file list")
        print(r.__dict__)
        raise click.Abort()
    file_list = r.json()["files"]
    file_list = {f["hash"]: f["id"] for f in file_list}
    for api_call in api_calls:
        if "check" not in api_call:
            continue
        if api_call["method"] == "PATCH":
            id_ = api_call["route"].split("/")[-1]
            hash_ = api_call["check"]
            if not (hash_ in file_list and file_list[hash_] == int(id_)):
                print(
                    (
                        "This commit would attempt to PATCH a resource that "
                        "not exist. (look at files with the merge action)"
                    )
                )
                raise click.Abort()
        if api_call["method"] == "POST":
            hash_ = api_call["check"]
            if hash_ in file_list:
                print(
                    (
                        "This commit would attempt to POST a new file which "
                        f"already exists (file_id: {file_list[hash_]})"
                    )
                )
                raise click.Abort()


def _do_commits(api_calls, cruise_id, basedir):
    """Actually do the API calls (asks for confirm)"""
    from cchdo.auth.session import session

    commit_lock = os.path.join(basedir, ".committed")
    if os.path.exists(commit_lock):
        print("This UOW has been commited, it cannot be committed again")
        raise click.Abort()
    print("!!Check the above to make sure it is what you want to do!!")
    print("Once the commit starts, allow the progam to exit itself")
    print(
        ("Depending on your network speed and commit size, it can take a long" "time")
    )

    click.confirm("Are you sure? (when in doubt, no)", abort=True)

    log_path = os.path.join(basedir, ".api_call_log")
    with open(commit_lock, "w") as f:
        f.write("incomplete")
    with open(log_path, "w") as f:
        connections = []
        print("uploading files and history note...")
        for api_call in api_calls:
            print(".")
            f.write(str(api_call) + "\n")
            route = f"{API_ENDPOINT}{api_call['route']}"

            if api_call["method"] == "PATCH":
                id_ = api_call["route"].split("/")[-1]
                r = session.patch(
                    route,
                    data=api_call["data"],
                )
                if r.status_code != 201:
                    print("Something has gone wrong with the last api call")
                    print(f"the api call log is: {log_path}")
                    print(r.__dict__)
                    raise click.Abort()
                if "file" in api_call["route"]:
                    connections.append((cruise_id, id_))
            if api_call["method"] == "POST":
                r = session.post(
                    route,
                    data=api_call["data"],
                )
                if r.status_code != 201:
                    print("Something has gone wrong with the last api call")
                    print(f"the api call log is: {log_path}")
                    print(r.__dict__)
                    raise click.Abort()
                id_ = r.json()["message"].split("/")[-1]
                if "file" in api_call["route"]:
                    connections.append((cruise_id, id_))
        print("upload done")
        print("connecting files to the cruise")
        for cruise_id, file_id in connections:
            route = f"{API_ENDPOINT}/cruise/{cruise_id}/files/{file_id}"

            f.write(f"POST {route}\n")
            r = session.post(route)
            if r.status_code != 201:
                print("Something went wrong with connecting files")
                print(f"the api call log is: {log_path}")
                print(r.__dict__)
                raise click.Abort()
    with open(commit_lock, "w") as f:
        f.write("done")
    print("commit done :)")


def do_commit():
    """Commit this UOW to CCHDO"""
    uow_info, basedir = get_uow_info()
    uow_json = load_uow_json()
    fetch_events = get_fetch_events()
    api_calls = _prepare_api_calls(uow_json, fetch_events, for_human=True)
    _check_api_calls_sanity(api_calls)
    _do_commits(api_calls, uow_info["cruise_id"], basedir)
