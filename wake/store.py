# ⏾🌊🛠 wake software's true potential
#
# Copyright (C) 2019 Rett Berg <github.com/vitiral>
#
# The source code is Licensed under either of
#
# * Apache License, Version 2.0, ([LICENSE-APACHE](LICENSE-APACHE) or
#   http://www.apache.org/licenses/LICENSE-2.0)
# * MIT license ([LICENSE-MIT](LICENSE-MIT) or
#   http://opensource.org/licenses/MIT)
#
# at your option.
#
# Unless you explicitly state otherwise, any contribution intentionally submitted
# for inclusion in the work by you, as defined in the Apache-2.0 license, shall
# be dual licensed as above, without any additional terms or conditions.
"""Functions for constructing a "wakestore" within the filesystem."""

import os
import shutil
import copy

from . import utils
from . import digest
from . import load


class Store(utils.SafeObject):
    """Basic store supporting CRUD operations."""
    def __init__(self, state):
        self.state = state
        self.temp_dir = self.state.create_temp_dir(prefix="store-")
        self.dir = self.temp_dir.dir
        self.packages = {}
        self.storeMap = {}

    def create_pkg(self, pkgDigest):
        """Insert a package into the store and return the result."""
        pkg_dir = os.path.join(self.dir, pkgDigest.pkgVer)

        if pkgDigest.pkgVer in self.packages:
            assert os.path.exists(pkg_dir)
            if self.packages[
                    pkgDigest.pkgVer].pkgVersion == pkgDigest.pkgVersion:
                return
            else:
                shutil.rmtree(pkg_dir)

        os.mkdir(pkg_dir)
        for path in pkgDigest.paths:
            src = os.path.join(pkgDigest.pkg_dir, path)
            dst = os.path.join(pkg_dir, path)
            shutil.copytree(src, dst, symlinks=True)

        result = self.read_pkg(pkgDigest.pkgVer)

        if pkgDigest.pkgVersion.digest != result.pkgVersion.digest:
            raise ValueError(
                "given pkgDigest had invalid digest value: {} != {}".format(
                    pkgDigest.pkgVersion.digest, result.pkgVersion.digest))

        self.packages[result.pkgVer] = result
        self.storeMap[result.pkgVer] = result.pkg_file
        return result

    def read_pkg(self, pkgVer):
        pkg_dir = os.path.join(self.dir, pkgVer)
        pkg_file = os.path.join(pkg_dir, FILE_PKG_DEFAULT)
        return load.loadPkgDigest(state, pkg_file, calc_digest=True)
