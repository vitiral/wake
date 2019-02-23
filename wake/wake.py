#!/usr/bin/python3
import sys, os
import argparse
import json
import subprocess

path = os.path
def abspath(p):
    return path.abspath(path.expanduser(p))

PATH_HERE = abspath(__file__)

wakelib = path.join(PATH_HERE, "lib", "wake.libsonnet")
with open(path.join(PATH_HERE, "lib", "wakeConstants.json")) as f:
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
local wakelib = import "{wakelib}/lib/wake.libsonnet";
local pkgDefs = (import "{pkg_wake}/pkgDefs.libsonnet");

local wake =
    wakelib
    + {{
        _private+: {{
            pkgDefs: pkgDefs,
        }},
    }};

// instantiate and return the root pkg
local pkg_fn = (import "{base}/PKG.libsonnet");
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
        self.pkg = path.join(self.base, "PKG.jsonnet")
        self.meta = path.join(self.base, "PKG.meta")
        self.pkg_wake = path.join(self.base, "_wake_")
        self.run = path.join(self.pkg_wake, "run.jsonnet")
        self.pkgs_defined = path.join(self.pkg_wake, "pkgsDefined.jsonnet")

        user_path = path.join(self.user_path, "user.jsonnet")
        if not path.exists(user_path):
            fail("must instantiate user credentials.")
        self.user = manifestJsonnet(user_path)

        self.store = path.join(self.user_path, self.user.get('store', 'store'))
        self.cache_defined = path.join(self.store, "pkgsDefined")

    def create_sandbox(self):
        """Create a simple linked sandbox."""
        assert path.exists(self.base)
        assert path.exists(self.pkg)
        assert path.exists(self.meta)

        os.mkdirs(self.pkg_wake, exist_ok=True)
        os.mkdirs(self.cache_defined, exist_ok=True)
        runtxt = RUN_TEMPLATE.format(
            wakelib=wakelib,
            base=self.base,
            pkg_wake=self.pkg_wake,
        )

        dump(self.run, runtxt)
        dump(self.pkgs_defined, "{}")


def build(args):
    # TODO: .wakeConfig.jsonnet
    config = Config()

    print("## building local pkg {}".format(config.base))



## Helpers

def manifestJsonnet(path):
    """Manifest a jsonnet path."""
    completed = subprocess.run(
        ["jsonnet", path],
        text=True,
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


## ARGUMENTS AND MAIN

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
