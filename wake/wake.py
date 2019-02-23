#!/usr/bin/python3
import sys, os
import argparse
import json
import subprocess

path = os.path

WAKEPATH = path.abspath(path.expanduser(os.getenv("WAKEPATH", "~/.wake")))
wakelib = path.join(WAKEPATH, "lib/wake.libsonnet")

def build(args):
    base = os.getcwd()
    print("## building local pkg {}".format(base))




## Helpers

def manifest(path):
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
