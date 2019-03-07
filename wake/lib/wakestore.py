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

    def add_pkg(self, pkg_config, simple_pkg, local=False):
        if local:
            pcache = pjoin(self.pkgs_local, simple_pkg.pkg_id)
        else:
            pcache = pjoin(self.pkgs, simple_pkg.pkg_id)

        if load_pkg_meta(pcache):
            return

        os.mkdir(pcache)
        wake_path = pjoin(pcache, DIR_WAKE)
        for fsentry_rel in simple_pkg.get_fsentries():
            assert_valid_path(fsentry_rel)
            fsentry_abs = pjoin(pcache, fsentry_rel)
            if fsentry_abs == wake_path:
                raise ValueError(
                    "package {} has .wake/ in its defFiles.".format(simple_pkg.pkg_id)
                )
            copy_fsentry(pkg_config.path_abs(fsentry_rel), fsentry_abs)

        copy_fsentry(pkg_config.pkg_fingerprint, pcache)
        meta = StoreMeta(state=S_DECLARED)
        jsondumpf(pkg_meta_path(pcache), meta.to_dict())

    def get_pkg_path(self, pkg_id, def_okay=False):
        pkg_str = str(pkg_id)
        pkgPath = pjoin(self.pkgs_local, pkg_str)
        if load_pkg_meta(pkgPath):
            return pkgPath

        pkgPath = pjoin(self.pkgs, pkg_str)
        if load_pkg_meta(pkgPath):
            return pkgPath

        if def_okay:
            pkgPath = pjoin(self.defined, pkg_str)
            if load_pkg_meta(pkgPath):
                return pkgPath

        return None


class StoreMeta(object):
    def __init__(self, state):
        self.state = state

    @classmethod
    def from_dict(cls, dct):
        return cls(
            state = dct['state'],
        )

    def to_dict(self):
        return {
            'state': self.state,
        }


def load_pkg_meta(pcache_path):
    if not os.path.exists(pcache_path):
        return None

    try:
        dct = jsonloadf(pkg_meta_path(pcache_path))
        return StoreMeta.from_dict(dct)
    except (json.decoder.JSONDecodeError, KeyError):
        # There was something at the path, but it was a partial pkg. It must be
        # removed.
        shutil.rmtree(pcache_path)
        return None


def pkg_meta_path(pcache_path):
    return path.join(pcache_path, DIR_WAKE, FILE_STORE_META)
