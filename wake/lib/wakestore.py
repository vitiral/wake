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

    def add_pkg_path(self, localpath):
        assert_valid_path(localpath)
        localconfig = PkgConfig(localpath)
        localpkg = localconfig.compute_simplepkg()
        localconfig.assert_meta_matches(localpkg)

        pcache = pjoin(self.pkgs, localpkg.pkg_id)

        if os.path.exists(pcache):
            pkg_exists = PkgConfig(pcache)
            metaexists = pkg_exists.get_current_meta()
            localconfig.assert_meta_matches(metaexists)
        else:
            assert path.exists(self.pkgs), self.pkgs
            os.mkdir(pcache)
            for fsentry_rel in localpkg.get_fsentries():
                assert_valid_path(fsentry_rel)
                copy_fsentry(localconfig.path_abs(fsentry_rel), path.join(pcache, fsentry_rel))

            # TODO: load, validate hash, validate that _wake_ doesn't exist, etc
            copy_fsentry(localconfig.pkg_meta, pcache)

