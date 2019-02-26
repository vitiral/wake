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


class Store(object):
    """
    (#SPC-arch.store): The default pkg and module storage boject.

    Stores objects on the local filesystem.
    """
    def __init__(self, base, store_dir):
        self.store_dir = store_dir
        self.defined = pjoin(self.store_dir, "pkgsDefined")
        self.pkgs = pjoin(self.store_dir, "pkgs")
        self.pkgs_local = path.join(base, ".wake", "pkgsLocal")

    def init_store(self):
        os.makedirs(self.pkgs_local, exist_ok=True)
        os.makedirs(self.defined, exist_ok=True)
        os.makedirs(self.pkgs, exist_ok=True)

    def remove_store(self):
        rmtree(self.pkgs_local)
        rmtree(self.defined)
        rmtree(self.pkgs)

    def add_pkg_path(self, pkg_config, simple_pkg, local=False):
        if local:
            pcache = pjoin(self.pkgs_local, simple_pkg.pkg_id)
        else:
            pcache = pjoin(self.pkgs, simple_pkg.pkg_id)

        if path.exists(pcache):
            return # TODO: check that it is done

        if os.path.exists(pcache):
            pkg_exists = PkgConfig(pcache)
            fingerprintexists = pkg_exists.get_current_fingerprint()
            # TODO: do this
            # pkg_config.assert_fingerprint_matches(fingerprintexists)
        else:
            assert path.exists(self.pkgs), self.pkgs
            os.mkdir(pcache)
            for fsentry_rel in simple_pkg.get_fsentries():
                assert_valid_path(fsentry_rel)
                copy_fsentry(pkg_config.path_abs(fsentry_rel), pjoin(pcache, fsentry_rel))

            # TODO: load, validate hash, validate that .wake doesn't exist, etc
            # TODO: write that state=done in fingerprint
            copy_fsentry(pkg_config.pkg_fingerprint, pcache)

    def get_pkg_path(self, pkg_id, def_okay=False):
        pkgPath = pjoin(self.pkgs_local, pkg_id)
        if os.path.exists(pkgPath):
            return pkgPath

        pkgPath = pjoin(self.pkgs, pkg_id)
        if os.path.exists(pkgPath):
            return pkgPath

        if def_okay:
            pkgPath = pjoin(self.defined, pkg_id)
            if os.path.exists(pkgPath):
                return pkgPath

        return None

