from wakedev import *
from wakehash import *


class PkgSimple(object):
    """Pull out only the data we care about."""
    def __init__(self, pkg_id, name, version, namespace, fingerprint, paths, def_paths):
        hash_ = fingerprint['hash']
        expected_pkg_id = [name, version, namespace, hash_]
        assert expected_pkg_id == pkg_id.split(','), (
            "pkgId != 'name,version,namespace,hash':\n{}\n{}".format(
                pkg_id, expected_pkg_id))

        assert_valid_paths(paths)
        assert_valid_paths(def_paths)

        self.pkg_root = "./PKG.libsonnet"
        self.pkg_id = pkg_id
        self.name = name
        self.namespace = namespace
        self.fingerprint = fingerprint

        self.paths = paths
        self.def_paths = def_paths

    @classmethod
    def from_dict(cls, dct):
        return cls(
            dct['pkgId'],
            dct['name'],
            dct['version'],
            dct['namespace'],
            dct['fingerprint'],
            dct['paths'],
            dct['defPaths'],
        )

    def get_def_fsentries(self):
        """Return all defined pkgs, including root."""
        return itertools.chain((self.pkg_root,), self.def_paths)

    def get_fsentries(self):
        return itertools.chain(self.get_def_fsentries(), self.paths)


class PkgConfig(object):
    def __init__(self, base):
        self.base = abspath(base)
        self.pkg_root = pjoin(self.base, "PKG.libsonnet")
        self.pkg_wake = pjoin(self.base, ".wake")
        self.pkg_meta = pjoin(self.pkg_wake, "fingerprint.json")
        self.run = pjoin(self.pkg_wake, "run.jsonnet")
        self.pkgs_defined = pjoin(self.pkg_wake, "pkgsDefined.jsonnet")

    def init_pkg_wake(self):
        """Create a simple linked sandbox."""
        assert path.exists(self.base)
        assert path.exists(self.pkg_root)

        os.makedirs(self.pkg_wake, exist_ok=True)
        runtxt = RUN_TEMPLATE.format(
            wakelib=wakelib,
            pkgs_defined=self.pkgs_defined,
            pkg_root=self.pkg_root,
        )

        dumpf(self.run, runtxt)
        dumpf(self.pkgs_defined, "{}")

    def remove_pkg_wake(self):
        if path.exists(self.pkg_wake):
            shutil.rmtree(self.pkg_wake)

    def get_current_meta(self):
        if not path.exists(self.pkg_meta):
            return None
        return jsonloadf(self.pkg_meta)

    def compute_pkg_meta(self):
        self.init_pkg_wake()
        root = self.compute_simplepkg()

        hashstuff = HashStuff(self.base)
        hashstuff.update_file(self.pkg_root)
        hashstuff.update_paths(self.paths_abs(root.paths))
        hashstuff.update_paths(self.paths_abs(root.def_paths))

        self.remove_pkg_wake()
        return {
            "hash": hashstuff.reduce(),
            "hashType": hashstuff.hash_type,
        }

    def path_abs(self, relpath):
        return pjoin(self.base, relpath)

    def paths_abs(self, relpaths):
        return map(self.path_abs, relpaths)

    def dump_pkg_meta(self):
        dumpf(self.pkg_meta, '{"hash": "--fake hash--", "hashType": "fake"}')
        meta = self.compute_pkg_meta()
        pp(meta)
        jsondumpf(self.pkg_meta, meta, indent=4)
        return meta

    def manifest_pkg(self):
        return manifest_jsonnet(self.run)

    def compute_simplepkg(self):
        """Use some shenanigans to get the pkg info."""
        self.init_pkg_wake()
        try:
            root = self.manifest_pkg()['root']
        finally:
            self.remove_pkg_wake()
        return PkgSimple.from_dict(root)

    def assert_meta_matches(self, pkgSimple, check_against=None):
        """Assert that the defined metas all match.

        pkgId should be the pkgId obtained from ``compute_simplepkg()``.
        """
        meta = self.get_current_meta()
        computed = self.compute_pkg_meta()
        assert meta == computed, "own meta does not match."

        if check_against is not None:
            assert meta == check_against

