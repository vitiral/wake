#!/usr/bin/python3

from wakedev import *
from wakepkg import *
from wakestore import *


class Config(object):
    def __init__(self):
        self.user_path = abspath(os.getenv("WAKEPATH", "~/.wake"))
        self.base = os.getcwd()

        self.pkg_config = PkgConfig(self.base)

        user_file = pjoin(self.user_path, "user.jsonnet")
        if not path.exists(user_file):
            fail("must instantiate user credentials: " + user_file)
        self.user = manifest_jsonnet(user_file)

        self.store = Store(pjoin(self.user_path, self.user.get('store', 'store')))

    def init_store(self):
        self.store.init_store()

    def remove_caches(self):
        self.pkg_config.remove_pkg_wake()
        self.store.remove_store()

    def handle_unresolved_pkg(self, pkg):
        from_ = pkg['from']
        if not isinstance(from_, str):
            raise NotYetImplementedError()
        else:
            # from_ is a path
            # TODO: something is wrong here... the path needs to be made absolute
            self.store.add_pkg_path(from_)

    def create_defined_pkgs(self, pkgs_defined):
        out = ["{"]

        # TODO: write jsonnet

        out.append("}")
        return "\n".join(out)



## COMMANDS AND MAIN

def run_cycle(config):
    pkg_config = config.pkg_config

    manifest = pkg_config.manifest_pkg()
    pkgs = manifest['all']

    num_unresolved = 0
    for pkg in pkgs:
        assert is_pkg(pkg)
        if is_unresolved(pkg):
            num_unresolved += 1
            config.handle_unresolved_pkg(pkg)


def build(args):
    config = Config()
    print("## building local pkg {}".format(config.base))
    pkg_config = config.pkg_config

    print("-> initializing the global cache")
    if MODE == DEBUG:
        config.remove_caches()
    config.init_store()

    print("-> recomputing PKG.meta")
    pkg_config.dump_pkg_meta()

    print("-> Starting build cycles")
    pkg_config.init_pkg_wake()

    # TODO: run in loop
    run_cycle(config)

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
