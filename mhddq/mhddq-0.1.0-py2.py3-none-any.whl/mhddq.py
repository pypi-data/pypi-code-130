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
def shutdown() -> None:
    _impl._shutdown()

#######################################################################
#         IS_SHUTDOWN                                                 #
#######################################################################
def is_shutdown() -> bool:
    return _impl._is_shutdown()

#######################################################################
#         DIRECTORY_EXISTS                                            #
#######################################################################
def directory_exists(callback: Callable, dirname: str) -> bool:
    return _impl._enqueue(_impl._directory_exists, { r'callback': callback, r'dirname': dirname })

#######################################################################
#         DIRECTORY_CREATE                                            #
#######################################################################
def directory_create(callback: Callable, dirname: str) -> bool:
    return _impl._enqueue(_impl._directory_create, { r'callback': callback, r'dirname': dirname })

#######################################################################
#         DIRECTORY_DELETE                                            #
#######################################################################
def directory_delete(callback: Callable, dirname: str) -> bool:
    return _impl._enqueue(_impl._directory_delete, { r'callback': callback, r'dirname': dirname })

#######################################################################
#         DIRECTORY_RENAME                                            #
#######################################################################
def directory_rename(callback: Callable, old_dirname: str, new_dirname: str) -> bool:
    return _impl._enqueue(_impl._directory_rename, { r'callback': callback, r'old_dirname': old_dirname, r'new_dirname': new_dirname })

#######################################################################
#         DIRECTORY_MOVE                                              #
#######################################################################
def directory_move(callback: Callable, source_dirname: str, destination_dirname: str) -> bool:
    return _impl._enqueue(_impl._directory_move, { r'callback': callback, r'source_dirname': source_dirname, r'destination_dirname': destination_dirname })

#######################################################################
#         DIRECTORY_COPY                                              #
#######################################################################
def directory_copy(callback: Callable, source_dirname: str, copy_dirname: str) -> bool:
    return _impl._enqueue(_impl._directory_copy, { r'callback': callback, r'source_dirname': source_dirname, r'copy_dirname': copy_dirname })

#######################################################################
#         DIRECTORY_CONTENTS                                          #
#######################################################################
def directory_contents(callback: Callable, dirname: str) -> bool:
    return _impl._enqueue(_impl._directory_contents, { r'callback': callback, r'dirname': dirname })

#######################################################################
#         FILE_EXISTS                                                 #
#######################################################################
def file_exists(callback: Callable, filename: str) -> bool:
    return _impl._enqueue(_impl._file_exists, { r'callback': callback, r'filename': filename })

#######################################################################
#         FILE_CREATE                                                 #
#######################################################################
def file_create(callback: Callable, filename: str) -> bool:
    return _impl._enqueue(_impl._file_create, { r'callback': callback, r'filename': filename })

#######################################################################
#         FILE_DELETE                                                 #
#######################################################################
def file_delete(callback: Callable, filename: str) -> bool:
    return _impl._enqueue(_impl._file_delete, { r'callback': callback, r'filename': filename })

#######################################################################
#         FILE_RENAME                                                 #
#######################################################################
def file_rename(callback: Callable, original_filename: str, new_filename: str) -> bool:
    return _impl._enqueue(_impl._file_rename, { r'callback': callback, r'original_filename': original_filename, r'new_filename': new_filename })

#######################################################################
#         FILE_MOVE                                                   #
#######################################################################
def file_move(callback: Callable, source_filename: str, destination_filename: str) -> bool:
    return _impl._enqueue(_impl._file_move, { r'callback': callback, r'source_filename': source_filename, r'destination_filename': destination_filename })

#######################################################################
#         FILE_COPY                                                   #
#######################################################################
def file_copy(callback: Callable, source_filename: str, copy_filename: str) -> bool:
    return _impl._enqueue(_impl._file_copy, { r'callback': callback, r'source_filename': source_filename, r'copy_filename': copy_filename })

#######################################################################
#         FILE_READ                                                   #
#######################################################################
def file_read(callback: Callable, filename: str, binary: bool = False) -> bool:
    return _impl._enqueue(_impl._file_read, { r'callback': callback, r'filename': filename, r'binary': binary })

#######################################################################
#         FILE_WRITE                                                  #
#######################################################################
def file_write(callback: Callable, data: Union[str, bytearray], filename: str, binary: bool = False) -> bool:
    return _impl._enqueue(_impl._file_write, { r'callback': callback, r'data': data, r'filename': filename, r'binary': binary })

#######################################################################
#         CREATE_EMPTY_OPLIST                                         #
#######################################################################
def create_empty_oplist() -> list:
    return []

#######################################################################
#         ENQUEUE_OPLIST                                              #
#######################################################################
def enqueue_oplist(oplist: list) -> bool:
    return _impl._enqueue(oplist, None)

#######################################################################
#         EMBED_OPLIST                                                #
#######################################################################
def embed_oplist(oplist: list, sub_oplist: list) -> None:
    oplist.append(sub_oplist)

#######################################################################
#         OPLIST_DIRECTORY_EXISTS                                     #
#######################################################################
def oplist_directory_exists(oplist: list, callback: Callable, dirname: str) -> None:
    oplist.append({ r'object': _impl._directory_exists, r'params': { r'callback': callback, r'dirname': dirname } })

#######################################################################
#         OPLIST_DIRECTORY_CREATE                                     #
#######################################################################
def oplist_directory_create(oplist: list, callback: Callable, dirname: str) -> None:
    oplist.append({ r'object': _impl._directory_create, r'params': { r'callback': callback, r'dirname': dirname } })

#######################################################################
#         OPLIST_DIRECTORY_DELETE                                     #
#######################################################################
def oplist_directory_delete(oplist: list, callback: Callable, dirname: str) -> None:
    oplist.append({ r'object': _impl._directory_delete, r'params': { r'callback': callback, r'dirname': dirname } })

#######################################################################
#         OPLIST_DIRECTORY_RENAME                                     #
#######################################################################
def oplist_directory_rename(oplist: list, callback: Callable, old_dirname: str, new_dirname: str) -> None:
    oplist.append({ r'object': _impl._directory_rename, r'params': { r'callback': callback, r'old_dirname': old_dirname, r'new_dirname': new_dirname } })

#######################################################################
#         OPLIST_DIRECTORY_MOVE                                       #
#######################################################################
def oplist_directory_move(oplist: list, callback: Callable, source_dirname: str, destination_dirname: str) -> None:
    oplist.append({ r'object': _impl._directory_move, r'params': { r'callback': callback, r'source_dirname': source_dirname, r'destination_dirname': destination_dirname } })

#######################################################################
#         OPLIST_DIRECTORY_COPY                                       #
#######################################################################
def oplist_directory_copy(oplist: list, callback: Callable, source_dirname: str, copy_dirname: str) -> None:
    oplist.append({ r'object': _impl._directory_copy, r'params': { r'callback': callback, r'source_dirname': source_dirname, r'copy_dirname': copy_dirname } })

#######################################################################
#         OPLIST_DIRECTORY_CONTENTS                                   #
#######################################################################
def oplist_directory_contents(oplist: list, callback: Callable, dirname: str) -> None:
    oplist.append({ r'object': _impl._directory_contents, r'params': { r'callback': callback, r'dirname': dirname } })

#######################################################################
#         OPLIST_FILE_EXISTS                                          #
#######################################################################
def oplist_file_exists(oplist: list, callback: Callable, filename: str) -> None:
    oplist.append({ r'object': _impl._file_exists, r'params': { r'callback': callback, r'filename': filename } })

#######################################################################
#         OPLIST_FILE_CREATE                                          #
#######################################################################
def oplist_file_create(oplist: list, callback: Callable, filename: str) -> None:
    oplist.append({ r'object': _impl._file_create, r'params': { r'callback': callback, r'filename': filename } })

#######################################################################
#         OPLIST_FILE_DELETE                                          #
#######################################################################
def oplist_file_delete(oplist: list, callback: Callable, filename: str) -> None:
    oplist.append({ r'object': _impl._file_delete, r'params': { r'callback': callback, r'filename': filename } })

#######################################################################
#         OPLIST_FILE_RENAME                                          #
#######################################################################
def oplist_file_rename(oplist: list, callback: Callable, original_filename: str, new_filename: str) -> None:
    oplist.append({ r'object': _impl._file_rename, r'params': { r'callback': callback, r'original_filename': original_filename, r'new_filename': new_filename } })

#######################################################################
#         OPLIST_FILE_MOVE                                            #
#######################################################################
def oplist_file_move(oplist: list, callback: Callable, source_filename: str, destination_filename: str) -> None:
    oplist.append({ r'object': _impl._file_move, r'params': { r'callback': callback, r'source_filename': source_filename, r'destination_filename': destination_filename } })

#######################################################################
#         OPLIST_FILE_COPY                                            #
#######################################################################
def oplist_file_copy(oplist: list, callback: Callable, source_filename: str, copy_filename: str) -> None:
    oplist.append({ r'object': _impl._file_copy, r'params': { r'callback': callback, r'source_filename': source_filename, r'copy_filename': copy_filename } })

#######################################################################
#         OPLIST_FILE_READ                                            #
#######################################################################
def oplist_file_read(oplist: list, callback: Callable, filename: str, binary: bool = False) -> None:
    oplist.append({ r'object': _impl._file_read, r'params': { r'callback': callback, r'filename': filename, r'binary': binary } })

#######################################################################
#         OPLIST_FILE_WRITE                                           #
#######################################################################
def oplist_file_write(oplist: list, callback: Callable, data: Union[str, bytearray], filename: str, binary: bool = False) -> None:
    oplist.append({ r'object': _impl._file_write, r'params': { r'callback': callback, r'data': data, r'filename': filename, r'binary': binary } })
