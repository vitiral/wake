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

        root_config = PkgConfig(self.base)
        self.pkgs_locked = pjoin(root_config.wakedir, "pkgsLocked.json")
        self.pkgs_defined = pjoin(root_config.wakedir, "pkgsDefined.jsonnet")
        self.run = pjoin(root_config.wakedir, "run.jsonnet")

        user_file = pjoin(self.user_path, "user.jsonnet")
        if not path.exists(user_file):
            fail("must instantiate user credentials: " + user_file)
        self.user = manifest_jsonnet(user_file)

        self.store = Store(
            self.base,
            pjoin(self.user_path, self.user.get('store', 'store')),
        )

    def init(self):
        self.store.init_store()

    def remove_caches(self):
        self.store.remove_store()

    def run_pkg(self, pkg_config, locked=None):
        locked = {} if locked is None else locked

        runtxt = RUN_TEMPLATE.format(
            wakelib=wakelib,
            pkgs_defined=self.pkgs_defined,
            pkg_root=pkg_config.pkg_root,
        )

        with open(self.pkgs_defined, 'w') as fd:
            fd.write("{\n")
            for pkg_key, pkg_id in locked.items():
                line = "  \"{}\": import \"{}/{}\",\n".format(
                    pkg_key,
                    self.store.get_pkg_path(pkg_id),
                    FILE_PKG,
                )
                fd.write(line)
            fd.write("}\n")
            os.fsync(fd)

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
        hashstuff.update_paths(pkg_config.paths_abs(root.paths_def))
        return Fingerprint(hash_=hashstuff.reduce(), hash_type=hashstuff.hash_type)

    def assert_fingerprint_matches(self, pkg_config):
        fingerprint = pkg_config.get_current_fingerprint()
        computed = self.compute_pkg_fingerprint(pkg_config)

        if fingerprint != computed:
            raise ValueError("fingerprints do no match:\nfingerprint.json={}\ncomputed={}".format(
                fingerprint,
                computed,
            ))

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
            out = self.store.get_pkg_path(pkg.pkg_req, def_okay=True)
            # TODO: to do this, I need the proper req tree
            # if out is None:
            #     raise ValueError("{} was not in the store".format(pkg))
            return out

    def create_defined_pkgs(self, pkgs_defined):
        out = ["{"]


        out.append("}")
        return "\n".join(out)


## COMMANDS AND MAIN

def run_cycle(config, root_config, locked):
    """Run a cycle with the config and root_config at the current setting."""
    manifest = config.run_pkg(root_config, locked)

    num_unresolved = 0
    for pkg in manifest.all:
        if isinstance(pkg, PkgUnresolved):
            num_unresolved += 1
            config.handle_unresolved_pkg(pkg)

    return (num_unresolved, manifest)

def store_local(config, local_abs, locked):
    """Recursively traverse local dependencies, putting them in the store.

    Also stores own version in the lockfile.
    """
    local_config = PkgConfig(local_abs)
    local_manifest = config.run_pkg(local_config)
    local_pkg = local_manifest.root
    local_key = local_pkg.get_pkg_key()
    if local_key in locked:
        raise ValueError("Attempted to add {} to local overrides twice.".format(local_key))

    # recursively store all local dependencies first
    deps = {}
    for dep in local_manifest.all:
        if dep.is_unresolved() and dep.is_from_local():
            deps[dep.from_] = store_local(
                config,
                pjoin(local_abs, dep.from_),
                locked,
            ).pkg_id

    deps = OrderedDict(sorted(deps.items()))

    # TODO: we must first write dependency lookups to local store and .wake/
    config.dump_pkg_fingerprint(local_config, deps)

    local_pkg = config.run_pkg(local_config).root
    if local_key in locked:
        raise ValueError("Attempted to add {} to local overrides twice.".format(local_key))
    locked[local_key] = local_pkg.pkg_id
    config.store.add_pkg(
        local_config,
        # Note: we don't pass deps here because we only care about hashes
        local_pkg,
        local=True,
    )

    return local_pkg


def build(args):
    config = Config()
    print("## building local pkg {}".format(config.base))
    root_config = PkgConfig(config.base)

    print("-> initializing the global cache")
    if MODE == DEBUG:
        config.remove_caches()
    root_config.init_wakedir()
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
    locked = {}
    store_local(config, config.base, locked)


    print("## BUILD CYCLES")

    cycle = 0
    unresolved = -1
    while unresolved:
        print("### CYCLE={}".format(cycle))
        print("-> locked pkgs")
        pp(locked)
        # TODO: run in loop
        new_unresolved, manifest = run_cycle(config, root_config, locked)

        print("-> manifest below. unresolved={}".format(new_unresolved))
        pp(manifest.to_dict())

        if unresolved == new_unresolved:
            fail("deadlock detected: unresolved has not changed for a cycle")
        unresolved = new_unresolved
        cycle += 1


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
    try:
        main(sys.argv)
    except:
        if MODE == DEBUG:
            import traceback, pdb
            extype, value, tb = sys.exc_info()
            traceback.print_exc()
            pdb.post_mortem(tb)
        else:
            raise

