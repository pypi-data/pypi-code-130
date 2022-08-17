import click

import os.path
import json
from urllib.parse import urlparse


from . import get_uow_info, API_ENDPOINT


def _load_files_metadata(file_ids):
    """Given a list of file ids, individually load all their metadata

    Ignoring the uow_info as some file_id may not be in there
    """
    from cchdo.auth.session import session

    file_metadata_list = []
    for file_id in file_ids:
        file_metadata_url = f"{API_ENDPOINT}/file/{file_id}"
        file_attach_list_url = f"{API_ENDPOINT}/file/{file_id}/cruises"

        cruise_list = session.get(file_attach_list_url)
        r = session.get(file_metadata_url)
        if not r.status_code == 200:
            print(
                (
                    "Something went wrong with the cruise metadata, "
                    "please include the following with the bug report:"
                )
            )
            print(r.__dict__)
            raise click.Abort()
        file_json = r.json()
        file_json["id"] = file_id
        if cruise_list.status_code == 200:
            file_json["__uow_crusie_list"] = cruise_list.json()["cruises"]
        file_metadata_list.append(file_json)
    return file_metadata_list


def _download_files_with_log(file_metadata_list, basedir):
    """Actually downloads the files from CCHDO

    Appends to a "fetch log" as this occurs
    """
    from cchdo.auth.session import session

    base_host = urlparse(API_ENDPOINT)
    base_host = f"{base_host.scheme}://{base_host.netloc}"
    log_path = os.path.join(basedir, ".fetch_log")
    for file_meta in file_metadata_list:
        url = f"{base_host}{file_meta['file_path']}"
        write_name = f"{file_meta['id']}_{file_meta['file_name']}"
        write_path = os.path.join(basedir, "0.existing_files", write_name)
        r = session.get(url, stream=True)
        if not r.status_code == 200:
            print(
                (
                    "Something went wrong with fetching a file, "
                    "please include the following with the bug report:"
                )
            )
            print(r.__dict__)
            raise click.Abort()

        # actually download the file
        with open(write_path, "wb") as f:
            # Sometimes the length is nothing, just have something REALLY long
            # so we don't spam the output with hashes
            # maybe figure out how pip does it, or figure out why the server
            # isn't seting a content length (cause it should be)
            total_length = int(r.headers.get("content-length", 10000000000000))
            with click.progressbar(
                r.iter_content(chunk_size=1024),
                length=(total_length / 1024) + 1,
                label=write_path + "  ",
            ) as chunks:
                for chunk in chunks:

                    if chunk:  # filter out keep-alive new chunks
                        f.write(chunk)
                        f.flush()
        # write our download event to the fetchlog
        # appending new lines to the begning and end avoids writing and invalid
        # json line in the event that a previous line didn't manage to write a
        # newline after itself
        with open(log_path, "a") as f:
            f.write("\n" + json.dumps(file_meta) + "\n")


def do_fetch(file_id, panic, external):
    """Fetch some files"""
    uow_info, basedir = get_uow_info()

    req_fids = set(file_id)
    known_fids = [int(id) for id in uow_info["file_metadata"].keys()]

    if panic:
        print(
            (
                "Panic! Downloading all cruise files, be sure to look in the "
                "'archive.tar' file for more data history."
            )
        )
        req_fids = set(known_fids)
    elif not all([id in known_fids for id in req_fids]) and not external:
        print("external files not allowed without the --external option")
        raise click.Abort()

    num_files = len(req_fids)
    print(f"Downloading {num_files} file{'s' if num_files > 1 else ''}")
    file_metadata_list = _load_files_metadata(req_fids)
    _download_files_with_log(file_metadata_list, basedir)
