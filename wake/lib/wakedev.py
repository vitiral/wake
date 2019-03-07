# Debug mode does things like delete folders before starting, etc

import sys, os
import argparse
import hashlib
import json
import subprocess
import shutil
import itertools
from collections import OrderedDict

from pprint import pprint as pp
from pdb import set_trace

DEBUG = "debug"
MODE = DEBUG

path = os.path

def pjoin(base, p):
    if p.startswith('./'):
        p = p[2:]
    return path.join(base, p)
def abspath(p):
    return path.abspath(path.expanduser(p))
def jsonloadf(path):
    with open(path) as fp:
        return json.load(fp)
def jsondumpf(path, data, indent=4):
    with open(path, 'w') as fp:
        return json.dump(
            data, fp,
            indent=indent,
            sort_keys=True)

PATH_HERE = abspath(__file__)
HERE_DIR = path.dirname(abspath(__file__))

wakelib = pjoin(HERE_DIR, "wake.libsonnet")
wakeConstants = jsonloadf(pjoin(HERE_DIR, "wakeConstants.json"))

WAKE_SEP = wakeConstants["WAKE_SEP"]

F_TYPE = wakeConstants["F_TYPE"]
F_STATE = wakeConstants["F_STATE"]
F_HASH = wakeConstants["F_HASH"]
F_HASHTYPE = wakeConstants["F_HASHTYPE"]

T_OBJECT = wakeConstants["T_OBJECT"]
T_PKG = wakeConstants["T_PKG"]
T_MODULE = wakeConstants["T_MODULE"]
T_FILE = wakeConstants["T_FILE"]

S_UNRESOLVED = wakeConstants["S_UNRESOLVED"]
S_DECLARED = wakeConstants["S_DECLARED"]
S_DEFINED = wakeConstants["S_DEFINED"]
S_COMPLETED = wakeConstants["S_COMPLETED"]

## COMMON PATHS

FILE_PKG = wakeConstants["FILE_PKG"]  # #SPC-arch.pkgFile

# See #SPC-arch.wakeDir
DIR_WAKE = wakeConstants["DIR_WAKE"]
DIR_WAKE_REL = path.join(".", DIR_WAKE)
DIR_LOCAL_STORE = wakeConstants["DIR_LOCAL_STORE"]

FILE_RUN = wakeConstants["FILE_RUN"]
FILE_PKG = wakeConstants["FILE_PKG"]
FILE_PKGS = wakeConstants["FILE_PKGS"]
FILE_STORE_META = "storeMeta.json"

FILE_FINGERPRINT = wakeConstants["FILE_FINGERPRINT"]
FILE_LOCAL_DEPENDENCIES = wakeConstants["FILE_LOCAL_DEPENDENCIES"]

## FILE WRITERS

RUN_TEMPLATE = """
local wakelib = import "{wakelib}";
local pkgsDefined = import "{pkgs_defined}";

local wake =
    wakelib
    + {{
        _private+: {{
            pkgsDefined: pkgsDefined,
        }},
    }};

// instantiate and return the root pkg
local pkg_fn = (import "{pkg_root}");
local pkgInitial = pkg_fn(wake);

local root = wake._private.recurseDefinePkg(wake, pkgInitial);

{{
    root: wake._private.simplify(root),
    all: wake._private.recurseSimplify(root),
}}
"""

def manifest_jsonnet(path):
    """Manifest a jsonnet path."""
    cmd = ["jsonnet", path]
    completed = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )
    if completed.returncode != 0:
        fail("Manifesting jsonnet at {}\n{}".format(path, completed.stderr))
    return json.loads(completed.stdout)


def fail(msg):
    msg = "FAIL: {}\n".format(msg)
    if MODE == DEBUG:
        raise RuntimeError(msg)
    else:
        sys.stderr.write(msg)
        sys.exit(1)


def dumpf(path, s):
    """Dump a string to a file."""
    with open(path, 'w') as f:
        f.write(s)

def copy_fsentry(src, dst):
    """Perform a deep copy on the filesystem entry (file, dir, symlink).

    This fully copies all files, following symlinks to copy the data.
    """
    dstdir = path.dirname(dst)
    if dstdir and not os.path.exists(dstdir):
        os.makedirs(dstdir, exist_ok=True)

    if path.isfile(src):
        shutil.copy(src, dst)
    else:
        shutil.copytree(src, dst)

def assert_valid_paths(paths):
    for p in paths:
        assert_valid_path(p)

def assert_valid_path(p):
    if not p.startswith("./"):
        raise ValueError("all paths must start with ./: " + p)
    if sum(filter(lambda c: c == '..', p.split('/'))):
        raise ValueError("paths must not have `..` components: " + p)

def assert_not_wake(p):
    if p.startswith(DIR_WAKE_REL):
        raise ValueError("paths must not start with {}: {}".format(DIR_WAKE_REL, p))


def is_pkg(dct):
    return dct[F_TYPE] == T_PKG


def is_unresolved(dct):
    return dct[F_STATE] == S_UNRESOLVED


def rmtree(d):
    if path.exists(d):
        shutil.rmtree(d)


def pkg_key(pkg_id):
    """Convert a pkg_id to the more general pkg_key."""



