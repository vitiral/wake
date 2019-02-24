#!/usr/bin/python3

from wakedev import *
from wakepkg import *
from wakestore import *


class Config(object):
    def __init__(self):
        self.user_path = abspath(os.getenv("WAKEPATH", "~/.wake"))
        self.base = os.getcwd()

        self.root_config = PkgConfig(self.base)
        self.pkgs_defined = pjoin(self.root_config.wakedir, "pkgsDefined.jsonnet")
        self.run = pjoin(self.root_config.wakedir, "run.jsonnet")

        user_file = pjoin(self.user_path, "user.jsonnet")
        if not path.exists(user_file):
            fail("must instantiate user credentials: " + user_file)
        self.user = manifest_jsonnet(user_file)

        self.store = Store(pjoin(self.user_path, self.user.get('store', 'store')))

    def init(self):
        self.root_config.init_wakedir()
        self.store.init_store()

    def remove_caches(self):
        self.store.remove_store()

    def run_pkg(self, pkg_config, pkgs_defined=None):
        pkgs_defined = {} if pkgs_defined is None else pkgs_defined

        runtxt = RUN_TEMPLATE.format(
            wakelib=wakelib,
            pkgs_defined=self.pkgs_defined,
            pkg_root=pkg_config.pkg_root,
        )

        with open(self.pkgs_defined, 'w') as fd:
            fd.write("{\n")
            for pkg_id, pkg_path_abs in pkgs_defined.items():
                line = "  \"{}\": import \"{}\",\n".format(
                    pkg_id,
                    pkg_path_abs
                )
                fd.write(line)
            fd.write("}\n")

        dumpf(self.run, runtxt)

        return manifest_jsonnet(self.run)

    def compute_pkg_meta(self, pkg_config):
        root = self.compute_simplepkg(pkg_config)

        hashstuff = HashStuff(pkg_config.base)
        hashstuff.update_file(pkg_config.pkg_root)
        hashstuff.update_paths(pkg_config.paths_abs(root.paths))
        hashstuff.update_paths(pkg_config.paths_abs(root.def_paths))
        return {
            "hash": hashstuff.reduce(),
            "hashType": hashstuff.hash_type,
        }

    def compute_simplepkg(self, pkg_config):
        """Use some shenanigans to get the pkg info."""
        root = self.run_pkg(pkg_config)['root']
        return PkgSimple.from_dict(root)

    def dump_pkg_meta(self, pkg_config):
        dumpf(pkg_config.pkg_meta, '{"hash": "--fake hash--", "hashType": "fake"}')
        meta = self.compute_pkg_meta(pkg_config)
        pp(meta)
        jsondumpf(pkg_config.pkg_meta, meta, indent=4)
        return meta

    def handle_unresolved_pkg(self, pkg):
        from_ = pkg['from']
        if not isinstance(from_, str):
            raise NotYetImplementedError()
        else:
            # from_ is a path
            # TODO: something is wrong here... the path needs to be made absolute
            pkg_config = PkgConfig(from_)
            self.dump_pkg_meta(pkg_config)
            pkg = self.compute_simplepkg(pkg_config)
            self.store.add_pkg_path(pkg_config, pkg)

    def create_defined_pkgs(self, pkgs_defined):
        out = ["{"]

        # TODO: write jsonnet

        out.append("}")
        return "\n".join(out)



## COMMANDS AND MAIN

def run_cycle(config):
    root_config = config.root_config

    manifest = config.run_pkg(root_config)
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
    root_config = config.root_config

    print("-> initializing the global cache")
    if MODE == DEBUG:
        config.remove_caches()
    config.init()

    print("-> recomputing .wake/fingerprint.json")
    config.dump_pkg_meta(root_config)

    print("-> Starting build cycles")
    # TODO: run in loop
    run_cycle(config)

    print("## MANIFEST")
    pp(config.run_pkg(root_config))


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
