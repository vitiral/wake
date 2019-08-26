# ⏾🌊🛠 wake software's true potential
#
# Copyright (C) 2019 Rett Berg <github.com/vitiral>
#
# The source code is Licensed under either of
#
# * Apache License, Version 2.0, ([LICENSE-APACHE](LICENSE-APACHE) or
#   http://www.apache.org/licenses/LICENSE-2.0)
# * MIT license ([LICENSE-MIT](LICENSE-MIT) or
#   http://opensource.org/licenses/MIT)
#
# at your option.
#
# Unless you explicitly state otherwise, any contribution intentionally submitted
# for inclusion in the work by you, as defined in the Apache-2.0 license, shall
# be dual licensed as above, without any additional terms or conditions.
"""
Debug mode does things like delete folders before starting, etc
"""

import sys
import os
import argparse
import hashlib
import json
import subprocess
import shutil
import itertools
from collections import OrderedDict

from pprint import pprint as pp
from pdb import set_trace

from . import constants


class SafeObject(object):
    """A safe form of ``object``.

    Does not allow hashes or comparisons by default.
    """
    def __hash__(self):
        raise TypeError("{} has no hash".format(self))

    def __eq__(self, _other):
        raise TypeError("{} cannot be compared".format(self))

    def __lt__(self, other):
        raise TypeError("{} cannot be compared".format(self))

    def __lte__(self, other):
        raise TypeError("{} cannot be compared".format(self))

    def __gt__(self, other):
        raise TypeError("{} cannot be compared".format(self))

    def __gte__(self, other):
        raise TypeError("{} cannot be compared".format(self))


class TupleObject(object):
    """An object which can be represented as a tuple for comparisons."""
    def _tuple(self):
        """Override this to return a tuple of only basic types."""
        raise NotImplementedError("Must implement _tuple")

    def _check_class(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError("Classes not comparable: {} with {}".format(
                self.__class__, other.__class__))

    def __hash__(self):
        return hash(self._tuple())

    def __eq__(self, other):
        self._check_class(other)
        return self._tuple() == other._tuple()

    def __lt__(self, other):
        self._check_class(other)
        return self._tuple() < other._tuple()

    def __lte__(self, other):
        self._check_class(other)
        return self._tuple() <= other._tuple()

    def __gt__(self, other):
        self._check_class(other)
        return self._tuple() > other._tuple()

    def __gte__(self, other):
        self._check_class(other)
        return self._tuple() >= other._tuple()


def pjoin(base, p):
    if p.startswith('./'):
        p = p[2:]
    return os.path.join(base, p)


def abspath(p):
    return os.path.abspath(path.expanduser(p))


def closefd(fd):
    """Really close a file descriptor for realz."""
    fd.flush()
    os.fsync(fd)


def loadf(path):
    with open(path) as fp:
        return fp.read()


def dumpf(path, text):
    with open(path, 'w') as fp:
        out = fp.write(text)
        closefd(fp)
        return out


def jsonloadf(path):
    with open(path) as fp:
        return json.load(fp)


def jsondumpf(path, data, indent=4):
    with open(path, 'w') as fp:
        out = json.dump(data, fp, indent=indent, sort_keys=True)
        closefd(fp)
        return out


def manifest_jsonnet(run_path):
    """Manifest a jsonnet run_path."""
    cmd = ["jsonnet", run_path]
    completed = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )
    if completed.returncode != 0:
        fail("Manifesting jsonnet at {}\n## STDOUT:\n{}\n\n## STDERR:\n{}\n".
             format(run_path, completed.stdout, completed.stderr))
    return json.loads(completed.stdout)


def format_run_digest(pkgFile):
    """Returned the wake jsonnet for creating the pkg digest."""
    templ = constants.RUN_DIGEST_TEMPLATE
    templ = templ.replace("WAKE_LIB", constants.PATH_WAKELIB)
    return templ.replace("PKG_FILE", pkgFile)


def format_run_export(pkgFile, pkgs_defined_path):
    """Returned the wake jsonnet for getting pkg exports."""
    templ = constants.RUN_EXPORT_TEMPLATE
    templ = templ.replace("WAKE_LIB", constants.PATH_WAKELIB)
    templ = templ.replace("PKG_FILE", pkgFile)
    return templ.replace("PKGS_DEFINED", pkgs_defined_path)


def fail(msg):
    msg = "FAIL: {}\n".format(msg)
    sys.stderr.write(msg)
    sys.exit(1)


def dumpf(path, s):
    """Dump a string to a file."""
    with open(path, 'w') as f:
        f.write(s)


def copytree(src, dst):
    """Allow copytree to copy files."""
    if os.path.isfile(src):
        shutil.copy2(src, dst)
    else:
        shutil.copytree(src, dst)


def ensure_valid_paths(paths):
    for p in paths:
        ensure_valid_path(p)

    return paths


def ensure_valid_path(p):
    if not p.startswith("./"):
        raise ValueError("all paths must start with ./: " + p)
    if sum(filter(lambda c: c == '..', p.split('/'))):
        raise ValueError("paths must not have `..` components: " + p)
    return p


def ensure_str(name, value, allow_none=False):
    if value is None and not allow_none:
        raise ValueError("{} not be null".format(name))
    return value


def assert_not_wake(p):
    if p.startswith(DIR_WAKE_REL):
        raise ValueError("paths must not start with {}: {}".format(
            DIR_WAKE_REL, p))


def is_pkg(dct):
    return dct[constants.F_TYPE] == constants.T_PKG


def is_path_pkg_ref(dct):
    return dct[constants.F_TYPE] == constants.T_PATH_REF_PKG


def is_unresolved(dct):
    return dct[constants.F_STATE] == constants.S_UNRESOLVED


def relpaths(paths, start):
    return [os.path.relpath(p, start=start) for p in paths]


def joinpaths(start, paths):
    return [os.path.join(start, p) for p in paths]


def rmtree(d):
    if os.path.exists(d):
        shutil.rmtree(d)


def walk(dirpath):
    """Walk the directory."""
    def _onerror(err):
        raise err

    return os.walk(dirpath, topdown=True, onerror=_onerror)
