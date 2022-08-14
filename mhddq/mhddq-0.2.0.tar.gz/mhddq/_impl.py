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
from copy import deepcopy
from datetime import datetime
from sys import stderr
from threading import Lock, Thread
from typing import Callable, Type, Union

import os
import shutil
import time

#######################################################################
#                                                                     #
#         _MHDDQ                                                      #
#                                                                     #
#######################################################################
class _mhddq:
    ###################################################################
    #         CLASS VARIABLES                                         #
    ###################################################################
    # this should NEVER be acquired by a _file_## or _directory_## function
    module_mutex: Type[Lock] = Lock()

    # this should ONLY be acquired by a _file_## or _directory_## function
    io_mutex: Type[Lock] = Lock()
    
    io_thread: list = None  # io threads
    io_queue: list = []  # io queue
    cb_thread: Type[Thread] = None  # callback thread
    cb_queue: list = []  # callback queue
    active: bool = True  # once set to False this can't be True again


#######################################################################
#                                                                     #
#         PRIVATE IMPLEMENTATION                                      #
#                                                                     #
#######################################################################
#######################################################################
#         _CB_THREADMAIN                                              #
#######################################################################
def _cb_threadmain() -> None:
    while True:
        _mhddq.module_mutex.acquire()

        if (
            _mhddq.active is False
            and 0 == len(_mhddq.io_queue)
            and 0 == len(_mhddq.cb_queue)
        ):
            _mhddq.module_mutex.release()

            # shutdown was initiated and all work is completed, time to exit the thread
            return

        if 0 < len(_mhddq.cb_queue):
            queue_empty: bool = False
            item = _mhddq.cb_queue.pop(0)

            # we can't control what the callback is doing so we are using a try block to
            # contain any exceptions and report them to stderr
            try:
                if callable(item[r'params'][r'callback']) is True:
                    item[r'params'][r'callback'](item)

                elif item[r'result'] is False:
                    # the callback is invalid but an exception was thrown during the operation
                    # instead of allowing the exception to fade into the abyss lets report it
                    print(
                        '[{0}] An exception was thrown during an IO operation with an invalid callback --\nMethod: {3}\nParams: {2}\nException: {1}'.format(
                            datetime.now().strftime('%m/%d %I:%M %p'),
                            str(item[r'output'][r'exception']),
                            str(item[r'params']),
                            str(item[r'action']),
                        ),
                        file=stderr,
                    )

            except Exception as cb_exception:
                print(
                    '[{0}] An exception was caught from during execution of an IO callback method --\nParams: {2}\nException: {1}'.format(
                        datetime.now().strftime('%m/%d %I:%M %p'),
                        str(cb_exception),
                        str(item),
                    ),
                    file=stderr,
                )

        else:
            queue_empty: bool = True

        _mhddq.module_mutex.release()

        if queue_empty is True:
            time.sleep(0.001)  # 1 millisecond

#######################################################################
#         _IO_THREADMAIN                                              #
#######################################################################
def _io_threadmain() -> None:
    while True:
        _mhddq.module_mutex.acquire()

        if _mhddq.active is False and 0 == len(_mhddq.io_queue):
            _mhddq.module_mutex.release()

            # shutdown was initiated and all the io work is completed, lets exit the thread
            return

        if 0 < len(_mhddq.io_queue):
            queue_empty: bool = False
            item = _mhddq.io_queue.pop(0)

            if type(item[r'object']) is list:
                _process_subqueue(item[r'object'])
                # a subqueue must be processed in it's entirety before moving on

            else:
                item[r'object'](item[r'params'])

        else:
            queue_empty: bool = True

        _mhddq.module_mutex.release()

        if queue_empty is True:
            time.sleep(0.001)  # 1 millisecond

#######################################################################
#         _PROCESS_SUBQUEUE                                           #
#######################################################################
def _process_subqueue(subqueue: list) -> None:
    while 0 < len(subqueue):
        item = subqueue.pop(0)

        if type(item) is list:
            _process_subqueue(item)

        else:
            item[r'object'](item[r'params'])

#######################################################################
#         _INIT                                                       #
#######################################################################
def _init() -> None:
    _mhddq.module_mutex.acquire()
    _mhddq.cb_thread = Thread(target=_cb_threadmain)
    _mhddq.cb_thread.start()
    _mhddq.io_thread = [Thread(target=_io_threadmain), Thread(target=_io_threadmain)]
    _mhddq.io_thread[0].start()
    _mhddq.io_thread[1].start()
    _mhddq.module_mutex.release()

#######################################################################
#         _SHUTDOWN                                                   #
#######################################################################
def _shutdown() -> None:
    _mhddq.module_mutex.acquire()

    if _mhddq.active is True:
        _mhddq.active = False
        _mhddq.module_mutex.release()

        _mhddq.io_thread[0].join()
        _mhddq.io_thread[1].join()
        _mhddq.cb_thread.join()

        _mhddq.module_mutex.acquire()
        _mhddq.io_thread = [None, None]
        _mhddq.cb_thread = None

    _mhddq.module_mutex.release()

#######################################################################
#         _IS_SHUTDOWN                                                #
#######################################################################
def _is_shutdown() -> bool:
    _mhddq.module_mutex.acquire()

    result: bool = _mhddq.cb_thread is None

    _mhddq.module_mutex.release()

    return result

#######################################################################
#         _ENQUEUE                                                    #
#######################################################################
def _enqueue(object: Union[Callable, list], params: dict) -> bool:
    _mhddq.module_mutex.acquire()

    if _mhddq.active is False:
        _mhddq.module_mutex.release()

        return False

    if _mhddq.io_thread is None:
        _mhddq.module_mutex.release()
        _init()  # initialize and start up the threads
        _mhddq.module_mutex.acquire()

    # all objects in an io queue must be a dict with these two keys
    _mhddq.io_queue.append({ r'object': object, r'params': params })
    _mhddq.module_mutex.release()

    return True

#######################################################################
#         _DIRECTORY_EXISTS                                           #
#######################################################################
def _directory_exists(params: dict) -> None:
    # params = { r'callback': Callable, 'dirname': str }
    result: bool = True

    _mhddq.io_mutex.acquire()

    try:
        output: dict = { r'exists': os.path.exists(params[r'dirname']) }

    except Exception as dir_exception:
        result: bool = False
        output: dict = { r'exception': str(dir_exception) }

    _mhddq.cb_queue.append(
        {
            r'action': r'directory_exists',
            r'result': result,
            r'params': params,
            r'output': output,
        }
    )
    _mhddq.io_mutex.release()

#######################################################################
#         _DIRECTORY_CREATE                                           #
#######################################################################
def _directory_create(params: dict) -> None:
    # params = { r'callback': Callable, 'dirname': str }
    result: bool = True
    output: dict = {}

    _mhddq.io_mutex.acquire()

    try:
        os.mkdir(params[r'dirname'])

    except Exception as dir_exception:
        result: bool = False
        output: dict = { r'exception': str(dir_exception) }

    _mhddq.cb_queue.append(
        {
            r'action': r'directory_create',
            r'result': result,
            r'params': params,
            r'output': output,
        }
    )
    _mhddq.io_mutex.release()

#######################################################################
#         _DIRECTORY_DELETE_CONTENTS                                  #
#######################################################################
def _directory_delete_contents(dirname: str) -> None:
    contents = os.listdir(dirname)

    for item in contents:
        full_path = os.path.join(dirname, item)

        if os.path.isfile(full_path) is True:
            os.remove(full_path)

        else:
            _directory_delete_contents(full_path)

            os.rmdir(full_path)

#######################################################################
#         _DIRECTORY_DELETE                                           #
#######################################################################
def _directory_delete(params: dict) -> None:
    # params = { r'callback': Callable, 'dirname': str }
    result: bool = True
    output: dict = {}

    _mhddq.io_mutex.acquire()

    try:
        _directory_delete_contents(params[r'dirname'])

        os.rmdir(params[r'dirname'])

    except Exception as dir_exception:
        result: bool = False
        output: dict = { r'exception': str(dir_exception) }

    _mhddq.cb_queue.append(
        {
            r'action': r'directory_delete',
            r'result': result,
            r'params': params,
            r'output': output,
        }
    )
    _mhddq.io_mutex.release()

#######################################################################
#         _DIRECTORY_RENAME                                           #
#######################################################################
def _directory_rename(params: dict) -> None:
    # params = { r'callback': Callable, 'old_dirname': str, 'new_dirname': str }
    result: bool = True
    output: dict = {}

    _mhddq.io_mutex.acquire()

    try:
        shutil.move(params[r'old_dirname'], params[r'new_dirname'])

    except Exception as dir_exception:
        result: bool = False
        output: dict = { r'exception': str(dir_exception) }

    _mhddq.cb_queue.append(
        {
            r'action': r'directory_rename',
            r'result': result,
            r'params': params,
            r'output': output,
        }
    )
    _mhddq.io_mutex.release()

#######################################################################
#         _DIRECTORY_MOVE                                             #
#######################################################################
def _directory_move(params: dict) -> None:
    # params = { r'callback': Callable, 'source_dirname': str, 'destination_dirname': str }
    result: bool = True
    output: dict = {}

    _mhddq.io_mutex.acquire()

    try:
        shutil.move(params[r'source_dirname'], params[r'destination_dirname'])

    except Exception as dir_exception:
        result: bool = False
        output: dict = { r'exception': str(dir_exception) }

    _mhddq.cb_queue.append(
        {
            r'action': r'directory_move',
            r'result': result,
            r'params': params,
            r'output': output,
        }
    )
    _mhddq.io_mutex.release()

#######################################################################
#         _DIRECTORY_COPY                                             #
#######################################################################
def _directory_copy(params: dict) -> None:
    # params = { r'callback': Callable, 'source_dirname': str, 'copy_dirname': str }
    result: bool = True
    output: dict = {}

    _mhddq.io_mutex.acquire()

    try:
        if os.path.exists(params[r'copy_dirname']) is True:
            raise FileExistsError

        for source_dir, subdirs, files in os.walk(params[r'source_dirname']):
            destination_dir = source_dir.replace(
                params[r'source_dirname'], params[r'copy_dirname'], 1
            )

            if not os.path.exists(destination_dir):
                os.makedirs(destination_dir)

            for file in files:
                source_file = os.path.join(source_dir, file)
                destination_file = os.path.join(destination_dir, file)

                if os.path.exists(destination_file) is True:
                    os.remove(destination_file)

                shutil.copy(source_file, destination_dir)

    except Exception as dir_exception:
        result: bool = False
        output: dict = { r'exception': str(dir_exception) }

    _mhddq.cb_queue.append(
        {
            r'action': r'directory_copy',
            r'result': result,
            r'params': params,
            r'output': output,
        }
    )
    _mhddq.io_mutex.release()

#######################################################################
#         _DIRECTORY_CONTENTS                                         #
#######################################################################
def _directory_contents(params: dict) -> None:
    # params = { r'callback': Callable, 'dirname': str }
    result: bool = True
    output: dict = { r'contents': [] }

    _mhddq.io_mutex.acquire()

    try:
        contents: list = os.listdir(params[r'dirname'])

        for item in contents:
            if os.path.isfile(os.path.join(params[r'dirname'], item)) is True:
                item_type: str = r'file'

            else:
                item_type: str = r'directory'

            output[r'contents'].append({r'name': item, r'type': item_type})

    except Exception as dir_exception:
        result: bool = False
        output: dict = { r'exception': str(dir_exception) }

    _mhddq.cb_queue.append(
        {
            r'action': r'directory_contents',
            r'result': result,
            r'params': params,
            r'output': output,
        }
    )
    _mhddq.io_mutex.release()

#######################################################################
#         _FILE_EXISTS                                                #
#######################################################################
def _file_exists(params: dict) -> None:
    # params = { r'callback': Callable, 'filename': str }
    result: bool = True

    _mhddq.io_mutex.acquire()

    try:
        output: dict = { r'exists': os.path.exists(params[r'filename']) }

    except Exception as file_exception:
        result: bool = False
        output: dict = { r'exception': str(file_exception) }

    _mhddq.cb_queue.append(
        {
            r'action': r'file_exists',
            r'result': result,
            r'params': params,
            r'output': output,
        }
    )
    _mhddq.io_mutex.release()

#######################################################################
#         _FILE_CREATE                                                #
#######################################################################
def _file_create(params: dict) -> None:
    # params = { r'callback': Callable, 'filename': str }
    result: bool = True
    output: dict = {}

    _mhddq.io_mutex.acquire()

    try:
        with open(params[r'filename'], r'x') as file:
            pass

    except Exception as file_exception:
        result: bool = False
        output: dict = { r'exception': str(file_exception) }

    _mhddq.cb_queue.append(
        {
            r'action': r'file_create',
            r'result': result,
            r'params': params,
            r'output': output,
        }
    )
    _mhddq.io_mutex.release()

#######################################################################
#         _FILE_DELETE                                                #
#######################################################################
def _file_delete(params: dict) -> None:
    # params = { r'callback': Callable, 'filename': str }
    result: bool = True
    output: dict = {}

    _mhddq.io_mutex.acquire()

    try:
        os.remove(params[r'filename'])

    except Exception as file_exception:
        result: bool = False
        output: dict = { r'exception': str(file_exception) }

    _mhddq.cb_queue.append(
        {
            r'action': r'file_delete',
            r'result': result,
            r'params': params,
            r'output': output,
        }
    )
    _mhddq.io_mutex.release()

#######################################################################
#         _FILE_RENAME                                                #
#######################################################################
def _file_rename(params: dict) -> None:
    # params = { r'callback': Callable, 'original_filename': str, 'new_filename': str }
    result: bool = True
    output: dict = {}

    _mhddq.io_mutex.acquire()

    try:
        os.rename(params[r'original_filename'], params[r'new_filename'])

    except Exception as file_exception:
        result: bool = False
        output: dict = { r'exception': str(file_exception) }

    _mhddq.cb_queue.append(
        {
            r'action': r'file_rename',
            r'result': result,
            r'params': params,
            r'output': output,
        }
    )
    _mhddq.io_mutex.release()

#######################################################################
#         _FILE_MOVE                                                  #
#######################################################################
def _file_move(params: dict) -> None:
    # params = { r'callback': Callable, 'source_filename': str, 'destination_filename': str }
    result: bool = True
    output: dict = {}

    _mhddq.io_mutex.acquire()

    try:
        shutil.move(params[r'source_filename'], params[r'destination_filename'])

    except Exception as file_exception:
        result: bool = False
        output: dict = { r'exception': str(file_exception) }

    _mhddq.cb_queue.append(
        {
            r'action': r'file_move',
            r'result': result,
            r'params': params,
            r'output': output,
        }
    )
    _mhddq.io_mutex.release()

#######################################################################
#         _FILE_COPY                                                  #
#######################################################################
def _file_copy(params: dict) -> None:
    # params = { r'callback': Callable, 'source_filename': str, 'copy_filename': str }
    result: bool = True
    output: dict = {}

    _mhddq.io_mutex.acquire()

    try:
        if os.path.exists(params[r'copy_filename']) is True:
            raise FileExistsError
            # shutil.copy2 hangs on Windows if the dest file already exists

        shutil.copy2(params[r'source_filename'], params[r'copy_filename'])

    except Exception as file_exception:
        result: bool = False
        output: dict = { r'exception': str(file_exception) }

    _mhddq.cb_queue.append(
        {
            r'action': r'file_copy',
            r'result': result,
            r'params': params,
            r'output': output,
        }
    )
    _mhddq.io_mutex.release()

#######################################################################
#         _FILE_READ                                                  #
#######################################################################
def _file_read(params: dict) -> None:
    # params = { r'callback': Callable, 'filename': str, 'binary': bool }
    result: bool = True

    _mhddq.io_mutex.acquire()

    try:
        if params[r'binary'] is True:
            file = open(params[r'filename'], r'rb')

        else:
            file = open(params[r'filename'], r'rt')

        output: dict = { r'data': file.read() }

        file.close()

    except Exception as file_exception:
        result: bool = False
        output: dict = { r'exception': str(file_exception) }

    _mhddq.cb_queue.append(
        {
            r'action': r'file_read',
            r'result': result,
            r'params': params,
            r'output': output,
        }
    )
    _mhddq.io_mutex.release()

#######################################################################
#         _FILE_WRITE                                                 #
#######################################################################
def _file_write(params: dict) -> None:
    # params = { r'callback': Callable, 'data': str|bytearray, 'filename': str, 'binary': bool }
    result: bool = True
    output: dict = {}

    _mhddq.io_mutex.acquire()

    try:
        if params[r'binary'] is True:
            file = open(params[r'filename'], r'wb')

        else:
            file = open(params[r'filename'], r'wt')

        file.write(params[r'data'])
        file.close()

    except Exception as file_exception:
        result: bool = False
        output: dict = { r'exception': str(file_exception) }

    _mhddq.cb_queue.append(
        {
            r'action': r'file_write',
            r'result': result,
            r'params': params,
            r'output': output,
        }
    )
    _mhddq.io_mutex.release()
