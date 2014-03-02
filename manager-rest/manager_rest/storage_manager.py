#########
# Copyright (c) 2013 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
#  * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  * See the License for the specific language governing permissions and
#  * limitations under the License.

__author__ = 'idanmo'

import imp
import sys
from os import path

from flask import g, current_app

from manager_rest.util import maybe_register_teardown

storage_manager_module_name = 'file_storage_manager'
#storage_manager_module_name = 'es_storage_manager'

_instance = None


def _create_instance():
    paths = sys.path
    paths.append(path.dirname(__file__))
    return imp.load_module(storage_manager_module_name,
                           *imp.find_module(
                               storage_manager_module_name, paths)).create()


def reset():
    # print "resetting storage"
    global _instance
    _instance = _create_instance()


def instance():
    global _instance
    if _instance is None:
        _instance = _create_instance()
    return _instance



def teardown_storage_manager(exception):
    # print "tearing down storage manager!"
    pass


def get_storage_manager():
    if 'storage_manager' not in g:
        g.storage_manager = _create_instance()  # TODO: make sure the import happens only once!
        maybe_register_teardown(current_app, teardown_storage_manager)

    return g.storage_manager


def get_storage_manager():
    return instance()

