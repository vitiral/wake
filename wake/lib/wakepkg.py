from wakedev import *
from wakehash import *

class PkgSimple(object):
    """Pull out only the data we care about."""
    def __init__(self, pkgId, paths, def_paths):
        self._assert_paths(paths)
        self._assert_paths(def_paths)

        self.pkgId = pkgId
        self.paths = paths
        self.def_paths = def_paths

    @classmethod
    def from_dict(cls, dct):
        return cls(
            dct['pkgId'],
            dct['paths'],
            dct['defPaths'],
        )

    def _assert_paths(self, paths):
        invalid_components = {'.', '..'}
        for p in paths:
            assert_valid_path(p)


class PkgConfig(object):
    def __init__(self, base):
        self.base = abspath(base)
        self.pkg_root = pjoin(self.base, "PKG.libsonnet")
        self.pkg_meta = pjoin(self.base, "PKG.meta")
        self.pkg_wake = pjoin(self.base, "_wake_")
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
        root = self.compute_root()

        hashstuff = HashStuff(self.base)
        hashstuff.update_file(self.pkg_root)
        hashstuff.update_paths(self.paths_abs(root.paths))
        hashstuff.update_paths(self.paths_abs(root.def_paths))

        self.remove_pkg_wake()
        return {
            "hash": hashstuff.reduce(),
            "hashType": hashstuff.hash_type,
        }

    def paths_abs(self, paths):
        return map(lambda p: pjoin(self.base, p), paths)

    def dump_pkg_meta(self):
        dumpf(self.pkg_meta, '{"hash": "--fake hash--", "hashType": "fake"}')
        meta = self.compute_pkg_meta()
        pp(meta)
        jsondumpf(self.pkg_meta, meta, indent=4)
        return meta

    def manifest_pkg(self):
        return manifest_jsonnet(self.run)

    def compute_root(self):
        """Use some shenanigans to get the pkg info."""
        self.init_pkg_wake()
        try:
            root = self.manifest_pkg()['root']
        finally:
            self.remove_pkg_wake()
        return PkgSimple.from_dict(root)
