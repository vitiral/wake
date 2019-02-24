from wakedev import *
from wakepkg import *


class Store(object):
    def __init__(self, store_dir):
        self.store_dir = store_dir
        self.defined = pjoin(self.store_dir, "pkgsDefined")
        self.pkgs = pjoin(self.store_dir, "pkgs")

    def init_store(self):
        os.makedirs(self.defined, exist_ok=True)
        os.makedirs(self.pkgs, exist_ok=True)

    def remove_store(self):
        rmtree(self.defined)
        rmtree(self.pkgs)

    def add_pkg_path(self, pkg_config, simple_pkg):
        pkg_config.assert_meta_matches(simple_pkg)

        pcache = pjoin(self.pkgs, simple_pkg.pkg_id)

        if os.path.exists(pcache):
            pkg_exists = PkgConfig(pcache)
            metaexists = pkg_exists.get_current_meta()
            pkg_config.assert_meta_matches(metaexists)
        else:
            assert path.exists(self.pkgs), self.pkgs
            os.mkdir(pcache)
            for fsentry_rel in simple_pkg.get_fsentries():
                assert_valid_path(fsentry_rel)
                copy_fsentry(pkg_config.path_abs(fsentry_rel), path.join(pcache, fsentry_rel))

            # TODO: load, validate hash, validate that .wake doesn't exist, etc
            copy_fsentry(pkg_config.pkg_meta, pcache)

