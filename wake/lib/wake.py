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

        manifest = manifest_jsonnet(self.run)
        return PkgManifest.from_dict(manifest)

    def compute_pkg_meta(self, pkg_config):
        root = self.run_pkg(pkg_config).root

        hashstuff = HashStuff(pkg_config.base)
        hashstuff.update_file(pkg_config.pkg_root)
        hashstuff.update_paths(pkg_config.paths_abs(root.paths))
        hashstuff.update_paths(pkg_config.paths_abs(root.def_paths))
        return Fingerprint(hash_=hashstuff.reduce(), hash_type=hashstuff.hash_type)

    def dump_pkg_meta(self, pkg_config):
        dumpf(pkg_config.pkg_meta, '{"hash": "--fake hash--", "hashType": "fake"}')
        fingerprint = self.compute_pkg_meta(pkg_config)
        jsondumpf(pkg_config.pkg_meta, fingerprint.to_dict(), indent=4)
        return fingerprint

    def handle_unresolved_pkg(self, pkg):
        from_ = pkg.from_
        if not isinstance(from_, str):
            raise NotYetImplementedError()
        else:
            # from_ is a path
            # TODO: something is wrong here... the path needs to be made absolute
            from_config = PkgConfig(from_)
            self.dump_pkg_meta(from_config)
            pkg = self.run_pkg(from_config).root
            self.store.add_pkg_path(from_config, pkg)

    def create_defined_pkgs(self, pkgs_defined):
        out = ["{"]

        # TODO: write jsonnet

        out.append("}")
        return "\n".join(out)



## COMMANDS AND MAIN

def run_cycle(config):
    root_config = config.root_config

    pkgs = config.run_pkg(root_config).all

    num_unresolved = 0
    for pkg in pkgs:
        if isinstance(pkg, PkgUnresolved):
            num_unresolved += 1
            config.handle_unresolved_pkg(pkg)


def store_local(config, base_path):
    """Recursively traverse local dependencies, putting them in the store.
    """
    base_config = PkgConfig(base_path)
    base_pkg = config.run_pkg(base_config)


def build(args):
    config = Config()
    print("## building local pkg {}".format(config.base))
    root_config = config.root_config

    print("-> initializing the global cache")
    if MODE == DEBUG:
        config.remove_caches()
    config.init()

    print("-> recomputing fingerprint")
    # TODO: this needs to be reworked. The solution also solves pkg overrides!
    # - Compute the hash of this pkg, by traversing all local dependencies
    #   first and computing their hashes
    # - When a local pkg's hash has been computed, put it in the `store.localPkgs`.
    #   This is a special place in the store that overrides pkgs for _only this
    #   directory_. (It is actually located in .wake/store/localPkgs). Also, the
    #   pkg names there don't include the hash (will be overriden if hash changes)
    # - This goes all the way down, until the rootPkg's hash has been computed and
    #   is stored in the local store.
    # - When retieving pkgs, we first check if the VERSION is in the local store.
    #   if it is, we take it.
    config.dump_pkg_meta(root_config)

    print("-> Starting build cycles")
    # TODO: run in loop
    run_cycle(config)

    print("## MANIFEST")
    pp(config.run_pkg(root_config).to_dict())


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
