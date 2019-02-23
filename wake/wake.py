#!/usr/bin/python3
import sys, os
import argparse
import hashlib
import json
import subprocess
import shutil
from pprint import pprint as pp

# Debug mode does things like delete folders before starting, etc
DEBUG = "debug"
MODE = DEBUG

path = os.path
pjoin = os.path.join
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

wakelib = pjoin(HERE_DIR, "lib", "wake.libsonnet")
wakeConstants = jsonloadf(pjoin(HERE_DIR, "lib", "wakeConstants.json"))

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

## FILE WRITERS

RUN_TEMPLATE = """
local wakelib = import "{wakelib}";
local pkgsDefined = (import "{pkgs_defined}");

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

def create_defined_pkgs(pkgs_defined):
    out = ["{"]

    # TODO: write jsonnet

    out.append("}")
    return "\n".join(out)


class PkgSimple(object):
    """Pull out only the data we care about."""
    def __init__(self, paths, def_paths):
        self._assert_paths(paths)
        self._assert_paths(def_paths)

        self.paths = paths
        self.def_paths = def_paths


    @classmethod
    def from_dict(cls, dct):
        return cls(
            dct['paths'],
            dct['defPaths'],
        )

    def _assert_paths(self, paths):
        invalid_components = {'.', '..'}
        for p in paths:
            if not p.startswith("./"):
                raise ValueError("all paths must start with ./")
            if sum(filter(lambda c: c == '..', p.split('/'))):
                raise ValueError("paths must not have `..` components: " + p)


class PkgConfig(object):
    def __init__(self, base):
        self.base = base
        self.pkg_root = pjoin(self.base, "PKG.libsonnet")
        self.pkg_meta = pjoin(self.base, "PKG.meta")
        self.pkg_wake = pjoin(self.base, "_wake_")
        self.run = pjoin(self.pkg_wake, "run.jsonnet")
        self.pkgs_defined = pjoin(self.pkg_wake, "pkgsDefined.jsonnet")

    def init_sandbox(self):
        """Create a simple linked sandbox."""
        assert path.exists(self.base)
        assert path.exists(self.pkg_root)
        assert path.exists(self.pkg_meta)

        os.makedirs(self.pkg_wake, exist_ok=True)
        runtxt = RUN_TEMPLATE.format(
            wakelib=wakelib,
            pkgs_defined=self.pkgs_defined,
            pkg_root=self.pkg_root,
        )

        dump(self.run, runtxt)
        dump(self.pkgs_defined, "{}")

    def remove_pkg_wake(self):
        if path.exists(self.pkg_wake):
            shutil.rmtree(self.pkg_wake)

    def get_current_meta(self):
        if not path.exists(self.pkg_meta):
            return None
        return jsonloadf(self.pkg_meta)

    def compute_pkg_meta(self):
        self.init_sandbox()
        root = PkgSimple.from_dict(self.manifest_pkg()['root'])

        hashstuff = HashStuff(self.base)
        hashstuff.update_file(self.pkg_root)
        hashstuff.update_paths(self.paths_abs(root.paths))
        hashstuff.update_paths(self.paths_abs(root.def_paths))

        return {
            "hash": hashstuff.reduce(),
            "hashType": hashstuff.hash_type,
        }

    def paths_abs(self, paths):
        return map(lambda p: pjoin(self.base, p), paths)

    def dump_pkg_meta(self):
        meta = self.compute_pkg_meta()
        pp(meta)
        jsondumpf(self.pkg_meta, meta, indent=4)
        return meta

    def manifest_pkg(self):
        return manifest_jsonnet(self.run)


class Config(object):
    def __init__(self):
        self.user_path = abspath(os.getenv("WAKEPATH", "~/.wake"))
        self.base = os.getcwd()

        self.pkg_config = PkgConfig(self.base)

        user_file = pjoin(self.user_path, "user.jsonnet")
        if not path.exists(user_file):
            fail("must instantiate user credentials: " + user_file)
        self.user = manifest_jsonnet(user_file)

        self.store = pjoin(self.user_path, self.user.get('store', 'store'))
        self.cache_defined = pjoin(self.store, "pkgsDefined")

    def init_sandbox(self):
        self.pkg_config.init_sandbox()
        os.makedirs(self.cache_defined, exist_ok=True)

    def remove_cache(self):
        self.pkg_config.remove_pkg_wake()
        if path.exists(self.cache_defined):
            for d in os.listdir(self.cache_defined):
                shutil.rmtree(d)


## Helpers

def manifest_jsonnet(path):
    """Manifest a jsonnet path."""
    cmd = ["jsonnet", path]
    print("calling", cmd)
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
    sys.stderr.write("FAIL: {}\n".format(msg))
    sys.exit(1)

def dump(path, s):
    """Dump a string to a file."""
    with open(path, 'w') as f:
        f.write(s)


# Heavily modified from checksumdir v1.1.5
# The MIT License (MIT)
# Copyright (c) 2015 cakepietoast
# https://pypi.org/project/checksumdir/#files

class HashStuff(object):
    HASH_TYPES = {
        'md5': hashlib.md5,
        'sha1': hashlib.sha1,
        'sha256': hashlib.sha256,
        'sha512': hashlib.sha512
    }

    def __init__(self, base, hash_type='md5'):
        assert path.isabs(base)

        self.base = base
        self.hash_type = hash_type
        self.hash_func = self.HASH_TYPES[hash_type]
        if not self.hash_func:
            raise NotImplementedError('{} not implemented.'.format(hash_type))
        self.hashmap = {}
        self.visited = set()

    @classmethod
    def from_config(cls, config):
        meta = config.get_current_meta()
        if meta is None:
            fail("{} meta file must exist".format(config.pkg_meta))
        return cls(config.base, hash_type=meta[F_HASHTYPE])

    def update_paths(self, paths):
        for p in paths:
            if path.isdir(p):
                self.update_dir(p)
            else:
                self.update_file(p)

    def update_dir(self, dirpath):
        assert path.isabs(dirpath), dirpath

        hash_func = self.hash_func
        hashmap = self.hashmap
        visited = self.visited

        if not os.path.isdir(dirpath):
            raise TypeError('{} is not a directory.'.format(dirpath))

        for root, dirs, files in os.walk(dirpath, topdown=True, followlinks=True):
            for f in files:
                fpath = pjoin(root, f)
                if fpath in visited:
                    raise RuntimeError(
                        "Error: infinite directory recursion detected at {}"
                        .format(fpath)
                    )
                visited.add(fpath)
                self.update_file(fpath)

        return hashmap

    def update_file(self, fpath):
        assert path.isabs(fpath)
        hasher = self.hash_func()
        blocksize = 64 * 1024
        with open(fpath, 'rb') as fp:
            while True:
                data = fp.read(blocksize)
                if not data:
                    break
                hasher.update(data)
        pkey = path.relpath(fpath, self.base)
        self.hashmap[pkey] = hasher.hexdigest()

    def reduce(self):
        hashmap = self.hashmap
        hasher = self.hash_func()
        for fpath in sorted(hashmap.keys()):
            hasher.update(fpath.encode())
            hasher.update(hashmap[fpath].encode())
        return hasher.hexdigest()


## COMMANDS AND MAIN

def build(args):
    # TODO: .wakeConfig.jsonnet
    config = Config()
    pkg_config = config.pkg_config
    print("## building local pkg {}".format(config.base))
    print("-> recomputing PKG.meta")
    pkg_config.dump_pkg_meta()

    if MODE == DEBUG:
        config.remove_cache()

    config.init_sandbox()

    print("## MANIFEST")
    pp(pkg_config.manifest_pkg())


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description='Wake: the pkg manager and build system of the web',
    )

    subparsers = parser.add_subparsers(help='[sub-command] help')
    parser_build = subparsers.add_parser(
        'build',
        help='build the pkg in the current directory'
    )
    parser_build.set_defaults(func=build)

    return parser.parse_args(argv)

def main(argv):
    args = parse_args(argv[1:])

    print(args)
    args.func(args)


if __name__ == '__main__':
    print(sys.argv)
    main(sys.argv)
