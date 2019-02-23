#!/usr/bin/python3
import sys, os
import argparse
import json
import subprocess
import shutil
from pprint import pprint as pp

# Debug mode does things like delete folders before starting, etc
DEBUG = "debug"
MODE = DEBUG

path = os.path
def abspath(p):
    return path.abspath(path.expanduser(p))

PATH_HERE = abspath(__file__)
HERE_DIR = path.dirname(abspath(__file__))

wakelib = path.join(HERE_DIR, "lib", "wake.libsonnet")
with open(path.join(HERE_DIR, "lib", "wakeConstants.json")) as f:
    wakeConstants = json.load(f)

F_TYPE = wakeConstants["F_TYPE"]
F_STATE = wakeConstants["F_STATE"]

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

local pkg = wake._private.recurseDefinePkg(wake, pkgInitial);

{{
    root: pkg,
}}
"""

def create_defined_pkgs(pkgs_defined):
    out = ["{"]

    # TODO: write jsonnet

    out.append("}")
    return "\n".join(out)


class Config(object):
    def __init__(self):
        self.user_path = abspath(os.getenv("WAKEPATH", "~/.wake"))
        self.base = os.getcwd()
        self.pkg_root = path.join(self.base, "PKG.libsonnet")
        self.pkg_meta = path.join(self.base, "PKG.meta")
        self.pkg_wake = path.join(self.base, "_wake_")
        self.run = path.join(self.pkg_wake, "run.jsonnet")
        self.pkgs_defined = path.join(self.pkg_wake, "pkgsDefined.jsonnet")

        user_file = path.join(self.user_path, "user.jsonnet")
        if not path.exists(user_file):
            fail("must instantiate user credentials: " + user_file)
        self.user = manifestJsonnet(user_file)

        self.store = path.join(self.user_path, self.user.get('store', 'store'))
        self.cache_defined = path.join(self.store, "pkgsDefined")

    def create_sandbox(self):
        """Create a simple linked sandbox."""
        assert path.exists(self.base)
        assert path.exists(self.pkg_root)
        assert path.exists(self.pkg_meta)

        os.makedirs(self.pkg_wake, exist_ok=True)
        os.makedirs(self.cache_defined, exist_ok=True)
        runtxt = RUN_TEMPLATE.format(
            wakelib=wakelib,
            pkgs_defined=self.pkgs_defined,
            pkg_root=self.pkg_root,
        )

        dump(self.run, runtxt)
        dump(self.pkgs_defined, "{}")


    def remove_cache(self):
        if path.exists(self.pkg_wake):
            shutil.rmtree(self.pkg_wake)

        if path.exists(self.cache_defined):
            for d in os.listdir(self.cache_defined):
                shutil.rmtree(d)

## Helpers

def manifestJsonnet(path):
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


## COMMANDS AND MAIN

def build(args):
    # TODO: .wakeConfig.jsonnet
    config = Config()

    print("## building local pkg {}".format(config.base))
    if MODE == DEBUG:
        config.remove_cache()

    config.create_sandbox()

    print("## MANIFEST")
    pp(manifestJsonnet(config.run))


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