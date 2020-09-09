# -*- coding: utf-8 -*-
#   Copyright 2019 Rett Berg (googberg@gmail.com)
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
"""Constants."""
from __future__ import unicode_literals

import os
import json
import six

######
# Utility functions (here because python2 disallows circular imports


def force_unicode(basic):
    """Force a basic value to be unicde recursively."""
    if not six.PY2 and isinstance(basic, bytes):
        raise ValueError("Cannot handle bytes.")

    if not six.PY2:
        # already unicode compatible
        return basic

    if isinstance(basic, (list, tuple, set)):
        return basic.__class__(force_unicode(v) for v in basic)
    if isinstance(basic, dict):
        return basic.__class__((force_unicode(k), force_unicode(v))
                               for k, v in six.iteritems(basic))
    if isinstance(basic, str):
        return basic.decode('utf-8')
    return basic


def loadf(path):
    with open(path) as fp:
        return force_unicode(fp.read())


def dumpf(path, string):
    """Dump a string to a file."""
    if isinstance(string, six.text_type):
        string = string.encode('utf-8')

    with open(path, 'wb') as f:
        f.write(string)


def jsonloadf(path):
    with open(path) as fp:
        return force_unicode(json.load(fp))


def jsondumpf(path, data, indent=4):
    with open(path, 'w') as fp:
        json.dump(data, fp, indent=indent, sort_keys=True)
        closefd(fp)


def closefd(fd):
    """Really close a file descriptor for realz."""
    fd.flush()
    os.fsync(fd)


######
# Constants
DIR_WAKELIB = os.path.dirname(os.path.abspath(__file__))
DEFAULT_FILE_DIGEST = ".wakeDigest.json"

_wakeConstants = jsonloadf(os.path.join(DIR_WAKELIB, "wakeConstants.json"))

WAKE_SEP = _wakeConstants["WAKE_SEP"]

F_TYPE = _wakeConstants["F_TYPE"]
F_STATE = _wakeConstants["F_STATE"]
F_DIGEST = _wakeConstants["F_DIGEST"]
F_DIGESTTYPE = _wakeConstants["F_DIGESTTYPE"]

T_OBJECT = _wakeConstants["T_OBJECT"]
T_PKG = _wakeConstants["T_PKG"]
T_MODULE = _wakeConstants["T_MODULE"]
T_PATH_REF_PKG = _wakeConstants["T_PATH_REF_PKG"]

S_UNRESOLVED = _wakeConstants["S_UNRESOLVED"]
S_DECLARED = _wakeConstants["S_DECLARED"]
S_DEFINED = _wakeConstants["S_DEFINED"]
S_COMPLETED = _wakeConstants["S_COMPLETED"]

C_READ_PKGS = _wakeConstants["C_READ_PKGS"]
C_READ_PKGS_REQ = _wakeConstants["C_READ_PKGS_REQ"]

DIR_WAKE = _wakeConstants["DIR_WAKE"]
FILE_WAKELIB = _wakeConstants["FILE_WAKELIB"]  #wake.libsonnet
FILE_PKG_DEFAULT = _wakeConstants["FILE_PKG_DEFAULT"]  # PKG.libsonnet
FILE_PKGS = _wakeConstants["FILE_PKGS"]
FILE_RUN_DIGEST = "wakeRunDigest.jsonnet"
FILE_RUN_EXPORT = "wakeRunExport.jsonnet"

# Common paths and data
PATH_WAKELIB = os.path.join(DIR_WAKELIB, FILE_WAKELIB)
_load_template = lambda f: loadf(os.path.join(DIR_WAKELIB, f))
RUN_DIGEST_TEMPLATE = _load_template(FILE_RUN_DIGEST)
RUN_EXPORT_TEMPLATE = _load_template(FILE_RUN_EXPORT)

# Common keys
K_DEPS = "deps"
K_DEPS_STR = "depsStrs"
K_PKG_NAME = "pkgName"
K_PKG_ORIGIN = "pkgOrigin"
K_PATHS = "paths"
K_EXPORT = "export"
