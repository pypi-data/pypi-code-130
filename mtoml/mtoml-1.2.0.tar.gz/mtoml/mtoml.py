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
from decimal import Decimal
from datetime import datetime
from sys import stderr
from threading import Lock
from typing import Any, Type

import copy
import os
import tomli
import tomli_w

#######################################################################
#     GET_DIR                                                         #
#######################################################################
def get_dir() -> str:
    mtomlc._mutex.acquire()

    directory = mtomlc._dir

    mtomlc._mutex.release()

    return directory

#######################################################################
#     SET_DIR                                                         #
#######################################################################
def set_dir(
    directory: str = r'./'
) -> bool:
    if os.path.exists(directory) is False:
        return False

    mtomlc._mutex.acquire()
    mtomlc._dir = directory
    mtomlc._mutex.release()

    return True

#######################################################################
#     LOAD                                                            #
#######################################################################
def load(
    config: str = None,
    force_reload: bool = False
) -> bool:
    file_data: dict = None

    if config is None:
        return False

    mtomlc._mutex.acquire()

    for file in mtomlc._files:
        if config.lower() == str(file[r'config']):
            if force_reload is False:
                mtomlc._mutex.release()

                print(
                    '[{0}] Configuration \'{1}\' failed to load due to previous unsaved changes. (force_reload: False)'.format(
                        datetime.now().strftime('%m/%d %I:%M %p'),
                        config,
                    ),
                    file = stderr,
                )

                return False

            try:
                with open(mtomlc._dir + config + r'.toml', r'rb') as toml_file:
                    file_data = tomli.load(toml_file, parse_float=Decimal)

            except Exception as toml_exception:
                print(
                    '[{0}] An exception was thrown while attempting to reload the configuration \'{1}\': {2}'.format(
                        datetime.now().strftime('%m/%d %I:%M %p'),
                        config,
                        str(toml_exception),
                    ),
                    file = stderr,
                )

            if file_data is None:
                mtomlc._mutex.release()

                print(
                    '[{0}] The configuration \'{1}\' failed to load.'.format(
                        datetime.now().strftime('%m/%d %I:%M %p'),
                        config,
                    ),
                    file = stderr,
                )

                return False

            file[r'data'] = file_data
            file[r'unsaved_changes'] = False

            mtomlc._mutex.release()

            print(
                '[{0}] Configuration \'{1}\' loaded successfully.'.format(
                    datetime.now().strftime('%m/%d %I:%M %p'),
                    config,
                ),
                file = stderr,
            )

            return True

    try:
        with open(mtomlc._dir + config + r'.toml', r'rb') as toml_file:
            file_data = tomli.load(toml_file, parse_float=Decimal)

    except Exception as toml_exception:
        print(
            '[{0}] An exception was thrown while attempting to load the configuration \'{1}\': {2}'.format(
                datetime.now().strftime('%m/%d %I:%M %p'),
                config,
                str(toml_exception),
            ),
            file = stderr,
        )

    if file_data is None:
        mtomlc._mutex.release()

        print(
            '[{0}] The configuration \'{1}\' failed to load.'.format(
                datetime.now().strftime('%m/%d %I:%M %p'),
                config,
            ),
            file = stderr,
        )

        return False

    mtoml_file = _mtoml_file(
        config = config.lower(),
        data = file_data
    )

    mtomlc._files.append(mtoml_file)
    mtomlc._mutex.release()

    print(
        '[{0}] Configuration \'{1}\' loaded successfully.'.format(
            datetime.now().strftime('%m/%d %I:%M %p'),
            config,
        ),
        file = stderr,
    )

    return True

#######################################################################
#     IS_LOADED                                                       #
#######################################################################
def is_loaded(
    config: str = None
) -> bool:
    if config is None:
        return False

    mtomlc._mutex.acquire()

    for file in mtomlc._files:
        if config.lower() == str(file[r'config']):
            mtomlc._mutex.release()

            return True

    mtomlc._mutex.release()

    return False

#######################################################################
#     SAVE                                                            #
#######################################################################
def save(
    config: str = None,
    force_overwrite: bool = False
) -> bool:
    is_valid_toml: bool = True

    if config is None:
        return False

    mtomlc._mutex.acquire()

    for file in mtomlc._files:
        if config.lower() == str(file[r'config']):
            if force_overwrite is False and file[r'unsaved_changes'] is False:
                mtomlc._mutex.release()

                return False

            try:
                tomli.loads(tomli_w.dumps(file[r'data']))

            except Exception as toml_exception:
                is_valid_toml = False

                print(
                    '[{0}] An exception was thrown while preparing to save the configuration \'{1}\': {2}'.format(
                        datetime.now().strftime('%m/%d %I:%M %p'),
                        config,
                        str(toml_exception),
                    ),
                    file = stderr,
                )

            if is_valid_toml is False:
                mtomlc._mutex.release()

                return False

            try:
                with open(mtomlc._dir + config + r'.toml', r'wb') as toml_file:
                    tomli_w.dump(file[r'data'], toml_file)

                file[r'unsaved_changes'] = False
                
            except Exception as toml_exception:
                is_valid_toml = False

                print(
                    '[{0}] An exception was thrown while saving the configuration \'{1}\': {2}'.format(
                        datetime.now().strftime('%m/%d %I:%M %p'),
                        config,
                        str(toml_exception),
                    ),
                    file = stderr,
                )

            mtomlc._mutex.release()

            return is_valid_toml

    mtomlc._mutex.release()

    print(
        '[{0}] The configuration \'{1}\' does not exist.'.format(
            datetime.now().strftime('%m/%d %I:%M %p'),
            config,
        ),
        file = stderr,
    )

    return False

#######################################################################
#     SAVE_ALL                                                        #
#######################################################################
def save_all(
    force_overwrite: bool = False
) -> bool:
    saved_all: bool = True

    mtomlc._mutex.acquire()

    for file in mtomlc._files:
        if force_overwrite is False and file[r'unsaved_changes'] is False:
            saved_all = False
                
            continue

        is_valid_toml: bool = True
            
        try:
            tomli.loads(tomli_w.dumps(file[r'data']))

        except Exception as toml_exception:
            is_valid_toml = False
            saved_all = False

            print(
                '[{0}] An exception was thrown while preparing to save the configuration \'{1}\': {2}'.format(
                    datetime.now().strftime('%m/%d %I:%M %p'),
                    str(file[r'config']),
                    str(toml_exception)
                ),
                file = stderr
            )

        if is_valid_toml is False:
            continue

        try:
            with open(mtomlc._dir + str(file[r'config']) + r'.toml', r'wb') as toml_file:
                tomli_w.dump(file[r'data'], toml_file)

            file[r'unsaved_changes'] = False
                
        except Exception as toml_exception:
            saved_all = False

            print(
                '[{0}] An exception was thrown while saving the configuration \'{1}\': {2}'.format(
                    datetime.now().strftime('%m/%d %I:%M %p'),
                    str(file[r'config']),
                    str(toml_exception),
                ),
                file = stderr,
            )

    mtomlc._mutex.release()

    return saved_all

#######################################################################
#     GET                                                             #
#######################################################################
def get(
    config: str = None,
    group: str = None,
    field: str = None
) -> Any:
    if config is None or field is None:
        return None

    mtomlc._mutex.acquire()

    for file in mtomlc._files:
        if config.lower() == str(file[r'config']):
            if group is None:
                if field in file[r'data'].keys():
                    value = file[r'data'][field]

                    mtomlc._mutex.release()

                    return value

            else:
                if group in file[r'data'].keys():
                    if type(file[r'data'][group]) is dict:
                        if field in file[r'data'][group].keys():
                            value = file[r'data'][group][field]

                            mtomlc._mutex.release()

                            return value

    mtomlc._mutex.release()

    return None

#######################################################################
#     SET                                                             #
#######################################################################
def set(
    config: str = None,
    group: str = None,
    field: str = None,
    value: Any = None
) -> bool:
    is_valid_toml: bool = True

    if config is None or field is None:
        return False

    mtomlc._mutex.acquire()

    for file in mtomlc._files:
        if config.lower() == str(file[r'config']):
            try:
                toml_copy = copy.deepcopy(file[r'data'])

                if group is None:
                    toml_copy[field] = value

                else:
                    if group not in toml_copy.keys():
                        toml_copy[group] = {}

                    toml_copy[group][field] = value

                # this will throw an exception if the modifications resulted in an invalid toml format
                tomli.loads(tomli_w.dumps(toml_copy))

                file[r'unsaved_changes'] = True
                file[r'data'] = toml_copy

            except Exception as toml_exception:
                is_valid_toml = False

                if group is None:
                    print(
                        '[{0}] The configuration \'{1}\' and field \'{2}\' attempted value set resulted in an invalid TOML format: {3}'.format(
                            datetime.now().strftime('%m/%d %I:%M %p'),
                            config,
                            field,
                            str(toml_exception),
                        ),
                        file = stderr,
                    )

                else:
                    print(
                        '[{0}] The configuration \'{1}\', group \'{3}\', and field \'{2}\' attempted group value set resulted in an invalid TOML format: {4}'.format(
                            datetime.now().strftime('%m/%d %I:%M %p'),
                            config,
                            field,
                            group,
                            str(toml_exception),
                        ),
                        file = stderr,
                    )

            mtomlc._mutex.release()

            return is_valid_toml

    mtomlc._mutex.release()

    print(
        '[{0}] The configuration \'{1}\' does not exist.'.format(
            datetime.now().strftime('%m/%d %I:%M %p'),
            config,
        ),
        file = stderr,
    )

    return False

#######################################################################
#         _MTOML_FILE                                                 #
#######################################################################
class _mtoml_file(dict):
    ###################################################################
    #     CONSTRUCTOR, INSTANCE VARIABLES                             #
    ###################################################################
    def __init__(self: r'_mtoml_file', config: str = None, data: dict = None):
        self[r'config'] = config
        self[r'unsaved_changes'] = False
        self[r'data'] = data

#######################################################################
#                                                                     #
#         MTOMLC                                                      #
#                                                                     #
#######################################################################
class mtomlc:
    ###################################################################
    #     CLASS VARIABLES                                             #
    ###################################################################
    _files: list[_mtoml_file] = []
    _dir: str = r'./'
    _mutex: Type[Lock] = Lock()

    ###################################################################
    #     CONSTRUCTOR, INSTANCE VARIABLES                             #
    ###################################################################
    def __init__(
        self: r'mtomlc',
        directory: str = r'./'
    ) -> None:
        if r'./' != directory:
            set_dir(directory)

    ###################################################################
    #     GET_DIR                                                     #
    ###################################################################
    def get_dir(
        self: r'mtomlc'
    ) -> str:
        return get_dir()

    ###################################################################
    #     SET_DIR                                                     #
    ###################################################################
    def set_dir(
        self: r'mtomlc',
        directory: str = r'./',
    ) -> bool:
        return set_dir(directory)

    ###################################################################
    #     LOAD                                                        #
    ###################################################################
    def load(
        self: r'mtomlc',
        config: str = None,
        force_reload: bool = False,
    ) -> bool:
        return load(config, force_reload)

    ###################################################################
    #     IS_LOADED                                                   #
    ###################################################################
    def is_loaded(
        self: r'mtomlc',
        config: str = None,
    ) -> bool:
        return is_loaded(config)

    ###################################################################
    #     SAVE                                                        #
    ###################################################################
    def save(
        self: r'mtomlc',
        config: str = None,
        force_overwrite: bool = False,
    ) -> bool:
        return save(config, force_overwrite)

    ###################################################################
    #     SAVE_ALL                                                    #
    ###################################################################
    def save_all(
        self: r'mtomlc',
        force_overwrite: bool = False,
    ) -> bool:
        return save_all(force_overwrite)

    ###################################################################
    #     GET                                                         #
    ###################################################################
    def get(
        self: r'mtomlc',
        config: str = None,
        group: str = None,
        field: str = None,
    ) -> Any:
        return get(
            config = config,
            group = group,
            field = field,
        )

    ###################################################################
    #     SET                                                         #
    ###################################################################
    def set(
        self: r'mtomlc',
        config: str = None,
        group: str = None,
        field: str = None,
        value: Any = None,
    ) -> bool:
        return set(
            config = config,
            group = group,
            field = field,
            value = value,
        )
