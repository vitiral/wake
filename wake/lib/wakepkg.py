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
        self.wakedir = pjoin(self.base, ".wake")
        self.pkg_meta = pjoin(self.wakedir, "fingerprint.json")

    def init_wakedir(self):
        assert path.exists(self.base)
        assert path.exists(self.pkg_root)
        os.makedirs(self.wakedir, exist_ok=True)

    def get_current_meta(self):
        if not path.exists(self.pkg_meta):
            return None
        return jsonloadf(self.pkg_meta)

    def path_abs(self, relpath):
        return pjoin(self.base, relpath)

    def paths_abs(self, relpaths):
        return map(self.path_abs, relpaths)

    def assert_meta_matches(self, pkgSimple, check_against=None):
        """Assert that the defined metas all match.

        pkgId should be the pkgId obtained from ``compute_simplepkg()``.
        """
        meta = self.get_current_meta()
        computed = self.compute_pkg_meta()
        assert meta == computed, "own meta does not match."

        if check_against is not None:
            assert meta == check_against

