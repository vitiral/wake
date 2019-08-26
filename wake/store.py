# -*- coding: utf-8 -*-
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

from __future__ import unicode_literals

import os
import shutil
import copy

from . import constants
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

    def create_pkg(self, pkgDigest):
        """Insert a package into the store and return the result."""
        pkgVerStr = pkgDigest.pkgVer.serialize()
        pkg_dir = os.path.join(self.dir, pkgVerStr)

        if pkgDigest.pkgVer in self.packages:
            assert os.path.exists(pkg_dir)
            existing = self.read_pkg(pkgDigest.pkgVer)
            if existing == pkgDigest.pkgVer:
                return existing
            else:
                shutil.rmtree(pkg_dir)

        os.mkdir(pkg_dir)
        for path in pkgDigest.paths:
            src = utils.pjoin(pkgDigest.pkg_dir, path)
            dst = utils.pjoin(pkg_dir, path)
            utils.copytree(src, dst)

        result = self.read_pkg(
            pkgDigest.pkgVer,
            skip_cache=True,
            check_cache=False,
        )

        if result.pkgVer.digest != pkgDigest.pkgVer.digest:
            raise ValueError(
                "The given pkgDigest had an invalid digest value: {} != {}".
                format(result.pkgVer.digest, pkgDigest.pkgVer.digest))

        self.packages[result.pkgVer] = result
        return result

    def read_pkg(self, pkgVer, skip_cache=False, check_cache=False):
        if skip_cache or check_cache:
            # TODO: on exception, delete the file
            pkg_dir = os.path.join(self.dir, pkgVer.serialize())
            pkg_file = os.path.join(pkg_dir, constants.FILE_PKG_DEFAULT)
            result = load.loadPkgDigest(self.state,
                                        pkg_file,
                                        calc_digest=True,
                                        cleanup=False)
            if check_cache:
                assert result.pkgVer == pkgVer
            return result

        return self.packages[pkgVer]
