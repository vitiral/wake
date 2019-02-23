#!/usr/bin/python3

from wakedev import *
from wakepkg import *


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
        self.cache_pkgs = pjoin(self.store, "pkgs")

    def init_cache(self):
        os.makedirs(self.cache_defined, exist_ok=True)
        os.makedirs(self.cache_pkgs, exist_ok=True)

    def remove_cache(self):
        self.pkg_config.remove_pkg_wake()
        rmtree(self.cache_defined)
        rmtree(self.cache_pkgs)

    def handle_unresolved_pkg(self, pkg):
        from_ = pkg['from']
        if not isinstance(from_, str):
            raise NotYetImplementedError()
        else:
            self.handle_unresolved_local_pkg(from_)

    def handle_unresolved_local_pkg(self, localpath):
        assert_valid_path(localpath)
        localconfig = PkgConfig(localpath)
        localpkg = localconfig.compute_root()
        localconfig.assert_meta_matches(localpkg)

        pcache = pjoin(self.cache_pkgs, localpkg.pkg_id)

        if os.path.exists(pcache):
            pkg_exists = PkgConfig(pcache)
            metaexists = pkg_exists.get_current_meta()
            localconfig.assert_meta_matches(metaexists)
        else:
            assert path.exists(self.cache_pkgs), self.cache_pkgs
            os.mkdir(pcache)

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
        config.remove_cache()
    config.init_cache()

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
