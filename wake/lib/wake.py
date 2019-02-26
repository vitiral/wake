#!/usr/bin/python3
#   Copyright 2019 Rett Berg (googberg@gmail.com)
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

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

        self.store = Store(
            self.base,
            pjoin(self.user_path, self.user.get('store', 'store')),
        )

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

    def compute_pkg_fingerprint(self, pkg_config):
        root = self.run_pkg(pkg_config).root

        hashstuff = HashStuff(pkg_config.base)
        if path.exists(pkg_config.path_local_deps):
            hashstuff.update_file(pkg_config.path_local_deps)

        hashstuff.update_file(pkg_config.pkg_root)
        hashstuff.update_paths(pkg_config.paths_abs(root.paths))
        hashstuff.update_paths(pkg_config.paths_abs(root.def_paths))
        return Fingerprint(hash_=hashstuff.reduce(), hash_type=hashstuff.hash_type)

    def dump_pkg_fingerprint(self, pkg_config, local_deps=None):
        local_deps = local_deps or {}
        jsondumpf(pkg_config.path_local_deps, local_deps)

        dumpf(pkg_config.pkg_fingerprint, '{"hash": "--fake hash--", "hashType": "fake"}')
        fingerprint = self.compute_pkg_fingerprint(pkg_config)
        jsondumpf(pkg_config.pkg_fingerprint, fingerprint.to_dict(), indent=4)
        return fingerprint

    def handle_unresolved_pkg(self, pkg):
        from_ = pkg.from_

        if not isinstance(from_, str):
            raise NotYetImplementedError()
        else:
            # It is a path, it must _already_ be in the store
            out = self.store.get_pkg_path(pkg.pkg_id, def_okay=True)
            if out is None:
                raise ValueError("{} was not in the store".format(pkg.pkg_id))
            return out

    def create_defined_pkgs(self, pkgs_defined):
        out = ["{"]


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


def store_local(config, local_abs):
    """Recursively traverse local dependencies, putting them in the store.
    """
    local_config = PkgConfig(local_abs)
    local_manifest = config.run_pkg(local_config)

    # recursively store all local dependencies first
    deps = {}
    for dep in local_manifest.all:
        if dep.is_unresolved() and dep.is_from_local():
            deps[dep.from_] = store_local(
                config,
                pjoin(local_abs, dep.from_)
            ).pkg_id

    deps = OrderedDict(sorted(deps.items()))

    # TODO: we must first write dependency lookups to local store and .wake/
    config.dump_pkg_fingerprint(local_config, deps)

    local_pkg = config.run_pkg(local_config).root
    config.store.add_pkg_path(
        local_config,
        # Note: we don't pass deps here because we only care about hashes
        local_pkg,
        local=True,
    )

    return local_pkg


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
    store_local(config, config.base)

    print("-> Starting build cycles")
    # TODO: run in loop
    # run_cycle(config)

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
