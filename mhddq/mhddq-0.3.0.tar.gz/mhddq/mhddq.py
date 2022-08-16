#######################################################################
# Copyright (c) 2022 Jordan Schaffrin                                 #
#                                                                     #
# This Source Code Form is subject to the terms of the Mozilla Public #
# License, v. 2.0. If a copy of the MPL was not distributed with this #
# file, You can obtain one at http://mozilla.org/MPL/2.0/.            #
#######################################################################

#######################################################################
#                                                                     #
#         IMPORTS                                                     #
#                                                                     #
#######################################################################
from typing import Callable, Union

import _impl

#######################################################################
#                                                                     #
#         PUBLIC API                                                  #
#                                                                     #
#######################################################################
#######################################################################
#         SHUTDOWN                                                    #
#######################################################################
def shutdown(
) -> None:
    _impl._shutdown()

#######################################################################
#         IS_SHUTDOWN                                                 #
#######################################################################
def is_shutdown(
) -> bool:
    return _impl._is_shutdown()

#######################################################################
#         DIRECTORY_EXISTS                                            #
#######################################################################
def directory_exists(
    callback: Callable,
    dirname: str
) -> bool:
    return _impl._enqueue(
        _impl._directory_exists,
        _impl._io_params(
            callback = callback,
            path = dirname,
        ),
    )

#######################################################################
#         DIRECTORY_CREATE                                            #
#######################################################################
def directory_create(
    callback: Callable,
    dirname: str
) -> bool:
    return _impl._enqueue(
        _impl._directory_create,
        _impl._io_params(
            callback = callback,
            path = dirname,
        ),
    )

#######################################################################
#         DIRECTORY_DELETE                                            #
#######################################################################
def directory_delete(
    callback: Callable,
    dirname: str
) -> bool:
    return _impl._enqueue(
        _impl._directory_delete,
        _impl._io_params(
            callback = callback,
            path = dirname,
        ),
    )

#######################################################################
#         DIRECTORY_RENAME                                            #
#######################################################################
def directory_rename(
    callback: Callable,
    old_dirname: str,
    new_dirname: str
) -> bool:
    return _impl._enqueue(
        _impl._directory_rename,
        _impl._io_params(
            callback = callback,
            path = old_dirname,
            target = new_dirname,
        ),
    )

#######################################################################
#         DIRECTORY_MOVE                                              #
#######################################################################
def directory_move(
    callback: Callable,
    source_dirname: str,
    destination_dirname: str
) -> bool:
    return _impl._enqueue(
        _impl._directory_move,
        _impl._io_params(
            callback = callback,
            path = source_dirname,
            target = destination_dirname,
        ),
    )

#######################################################################
#         DIRECTORY_COPY                                              #
#######################################################################
def directory_copy(
    callback: Callable,
    source_dirname: str,
    copy_dirname: str
) -> bool:
    return _impl._enqueue(
        _impl._directory_copy,
        _impl._io_params(
            callback = callback,
            path = source_dirname,
            target = copy_dirname,
        ),
    )

#######################################################################
#         DIRECTORY_CONTENTS                                          #
#######################################################################
def directory_contents(
    callback: Callable,
    dirname: str
) -> bool:
    return _impl._enqueue(
        _impl._directory_contents,
        _impl._io_params(
            callback = callback,
            path = dirname,
        ),
    )

#######################################################################
#         FILE_EXISTS                                                 #
#######################################################################
def file_exists(
    callback: Callable,
    filename: str
) -> bool:
    return _impl._enqueue(
        _impl._file_exists,
        _impl._io_params(
            callback = callback,
            path = filename,
        ),
    )

#######################################################################
#         FILE_CREATE                                                 #
#######################################################################
def file_create(
    callback: Callable,
    filename: str
) -> bool:
    return _impl._enqueue(
        _impl._file_create,
        _impl._io_params(
            callback = callback,
            path = filename,
        ),
    )

#######################################################################
#         FILE_DELETE                                                 #
#######################################################################
def file_delete(
    callback: Callable,
    filename: str
) -> bool:
    return _impl._enqueue(
        _impl._file_delete,
        _impl._io_params(
            callback = callback,
            path = filename,
        ),
    )

#######################################################################
#         FILE_RENAME                                                 #
#######################################################################
def file_rename(
    callback: Callable,
    original_filename: str,
    new_filename: str
) -> bool:
    return _impl._enqueue(
        _impl._file_rename,
        _impl._io_params(
            callback = callback,
            path = original_filename,
            target = new_filename,
        ),
    )

#######################################################################
#         FILE_MOVE                                                   #
#######################################################################
def file_move(
    callback: Callable,
    source_filename: str,
    destination_filename: str
) -> bool:
    return _impl._enqueue(
        _impl._file_move,
        _impl._io_params(
            callback = callback,
            path = source_filename,
            target = destination_filename,
        ),
    )

#######################################################################
#         FILE_COPY                                                   #
#######################################################################
def file_copy(
    callback: Callable,
    source_filename: str,
    copy_filename: str
) -> bool:
    return _impl._enqueue(
        _impl._file_copy,
        _impl._io_params(
            callback = callback,
            path = source_filename,
            target = copy_filename,
        ),
    )

#######################################################################
#         FILE_READ                                                   #
#######################################################################
def file_read(
    callback: Callable,
    filename: str,
    binary: bool = False
) -> bool:
    return _impl._enqueue(
        _impl._file_read,
        _impl._io_params(
            callback = callback,
            path = filename,
            option = binary,
        ),
    )

#######################################################################
#         FILE_WRITE                                                  #
#######################################################################
def file_write(
    callback: Callable,
    data: Union[str, bytearray],
    filename: str,
    binary: bool = False
) -> bool:
    return _impl._enqueue(
        _impl._file_write,
        _impl._io_params(
            callback = callback,
            path = filename,
            target = data,
            option = binary,
        ),
    )

#######################################################################
#         CREATE_EMPTY_OPLIST                                         #
#######################################################################
def create_empty_oplist(
) -> list:
    # using a function for this just in case the oplist type changes in
    # the future it won't require any rewrites for code using mhddq
    return []

#######################################################################
#         CLEAR_OPLIST                                                #
#######################################################################
def clear_oplist(
    oplist: list
) -> None:
    oplist.clear()

#######################################################################
#         ENQUEUE_OPLIST                                              #
#######################################################################
def enqueue_oplist(
    oplist: list
) -> bool:
    return _impl._enqueue(oplist, None)

#######################################################################
#         EMBED_OPLIST                                                #
#######################################################################
def embed_oplist(
    oplist: list,
    sub_oplist: list
) -> None:
    oplist.append(sub_oplist)

#######################################################################
#         OPLIST_DIRECTORY_EXISTS                                     #
#######################################################################
def oplist_directory_exists(
    oplist: list,
    callback: Callable,
    dirname: str
) -> None:
    oplist.append(
        _impl._io_item(
            object = _impl._directory_exists,
            params = _impl._io_params(
                callback = callback,
                path = dirname,
            ),
        ),
    )

#######################################################################
#         OPLIST_DIRECTORY_CREATE                                     #
#######################################################################
def oplist_directory_create(
    oplist: list,
    callback: Callable,
    dirname: str
) -> None:
    oplist.append(
        _impl._io_item(
            object = _impl._directory_create,
            params = _impl._io_params(
                callback = callback,
                path = dirname,
            ),
        ),
    )

#######################################################################
#         OPLIST_DIRECTORY_DELETE                                     #
#######################################################################
def oplist_directory_delete(
    oplist: list,
    callback: Callable,
    dirname: str
) -> None:
    oplist.append(
        _impl._io_item(
            object = _impl._directory_delete,
            params = _impl._io_params(
                callback = callback,
                path = dirname,
            ),
        ),
    )

#######################################################################
#         OPLIST_DIRECTORY_RENAME                                     #
#######################################################################
def oplist_directory_rename(
    oplist: list,
    callback: Callable,
    old_dirname: str,
    new_dirname: str
) -> None:
    oplist.append(
        _impl._io_item(
            object = _impl._directory_rename,
            params = _impl._io_params(
                callback = callback,
                path = old_dirname,
                target = new_dirname,
            ),
        ),
    )

#######################################################################
#         OPLIST_DIRECTORY_MOVE                                       #
#######################################################################
def oplist_directory_move(
    oplist: list,
    callback: Callable,
    source_dirname: str,
    destination_dirname: str
) -> None:
    oplist.append(
        _impl._io_item(
            object = _impl._directory_move,
            params = _impl._io_params(
                callback = callback,
                path = source_dirname,
                target = destination_dirname,
            ),
        ),
    )

#######################################################################
#         OPLIST_DIRECTORY_COPY                                       #
#######################################################################
def oplist_directory_copy(
    oplist: list,
    callback: Callable,
    source_dirname: str,
    copy_dirname: str
) -> None:
    oplist.append(
        _impl._io_item(
            object = _impl._directory_copy,
            params = _impl._io_params(
                callback = callback,
                path = source_dirname,
                target = copy_dirname,
            ),
        ),
    )

#######################################################################
#         OPLIST_DIRECTORY_CONTENTS                                   #
#######################################################################
def oplist_directory_contents(
    oplist: list,
    callback: Callable,
    dirname: str
) -> None:
    oplist.append(
        _impl._io_item(
            object = _impl._directory_copy,
            params = _impl._io_params(
                callback = callback,
                path = dirname,
            ),
        ),
    )

#######################################################################
#         OPLIST_FILE_EXISTS                                          #
#######################################################################
def oplist_file_exists(
    oplist: list,
    callback: Callable,
    filename: str
) -> None:
    oplist.append(
        _impl._io_item(
            object = _impl._file_exists,
            params = _impl._io_params(
                callback = callback,
                path = filename,
            ),
        ),
    )

#######################################################################
#         OPLIST_FILE_CREATE                                          #
#######################################################################
def oplist_file_create(
    oplist: list,
    callback: Callable,
    filename: str
) -> None:
    oplist.append(
        _impl._io_item(
            object = _impl._file_create,
            params = _impl._io_params(
                callback = callback,
                path = filename,
            ),
        ),
    )

#######################################################################
#         OPLIST_FILE_DELETE                                          #
#######################################################################
def oplist_file_delete(
    oplist: list,
    callback: Callable,
    filename: str
) -> None:
    oplist.append(
        _impl._io_item(
            object = _impl._file_delete,
            params = _impl._io_params(
                callback = callback,
                path = filename,
            ),
        ),
    )

#######################################################################
#         OPLIST_FILE_RENAME                                          #
#######################################################################
def oplist_file_rename(
    oplist: list,
    callback: Callable,
    original_filename: str,
    new_filename: str
) -> None:
    oplist.append(
        _impl._io_item(
            object = _impl._file_rename,
            params = _impl._io_params(
                callback = callback,
                path = original_filename,
                target = new_filename,
            ),
        ),
    )

#######################################################################
#         OPLIST_FILE_MOVE                                            #
#######################################################################
def oplist_file_move(
    oplist: list,
    callback: Callable,
    source_filename: str,
    destination_filename: str
) -> None:
    oplist.append(
        _impl._io_item(
            object = _impl._file_move,
            params = _impl._io_params(
                callback = callback,
                path = source_filename,
                target = destination_filename,
            ),
        ),
    )

#######################################################################
#         OPLIST_FILE_COPY                                            #
#######################################################################
def oplist_file_copy(
    oplist: list,
    callback: Callable,
    source_filename: str,
    copy_filename: str
) -> None:
    oplist.append(
        _impl._io_item(
            object = _impl._file_copy,
            params = _impl._io_params(
                callback = callback,
                path = source_filename,
                target = copy_filename,
            ),
        ),
    )

#######################################################################
#         OPLIST_FILE_READ                                            #
#######################################################################
def oplist_file_read(
    oplist: list,
    callback: Callable,
    filename: str,
    binary: bool = False
) -> None:
    oplist.append(
        _impl._io_item(
            object = _impl._file_read,
            params = _impl._io_params(
                callback = callback,
                path = filename,
                option = binary,
            ),
        ),
    )

#######################################################################
#         OPLIST_FILE_WRITE                                           #
#######################################################################
def oplist_file_write(
    oplist: list,
    callback: Callable,
    data: Union[str, bytearray],
    filename: str,
    binary: bool = False,
) -> None:
    oplist.append(
        _impl._io_item(
            object = _impl._file_write,
            params = _impl._io_params(
                callback = callback,
                path = filename,
                target = data,
                option = binary,
            ),
        ),
    )
