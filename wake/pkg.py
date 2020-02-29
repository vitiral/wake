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
"""Pkg types."""
from __future__ import unicode_literals

import os

from . import constants as C
from . import utils
from . import digest


class PkgName(utils.TupleObject):
    """The namespace and name of a package."""
    def __init__(self, namespace, name, patch):
        self.namespace = namespace
        self.name = name
        self.patch = patch

    def __str__(self):
        return C.WAKE_SEP.join((self.namespace, self.name, self.patch))

    def __repr__(self):
        return "name:{}".format(self)

    def _tuple(self):
        return (self.namespace, self.name, self.patch)


class PkgDigest(utils.SafeObject):
    """The items which are used in the pkg digest.

    These items must completely define the package for transport and use.
    """

    # pylint: disable=too-many-arguments
    def __init__(self, pkg_file, pkgName, pkgOrigin, paths, depNames, digest):
        if pkg_file not in paths:
            paths.add('./' + C.FILE_PKG_DEFAULT)

        self.pkg_file = pkg_file
        self.pkg_dir = os.path.dirname(pkg_file)
        self.pkg_digest = os.path.join(self.pkg_dir,
                                       C.DEFAULT_FILE_DIGEST)
        self.pkgName = pkgName
        self.pkgOrigin = pkgOrigin
        self.paths = paths
        self.depNames = depNames
        self.digest = digest

    @classmethod
    def deserialize(cls, dct, pkg_file):
        """Derialize."""
        pkg_ver_str = utils.ensure_str(C.K_PKG_NAME, dct[C.K_PKG_NAME])
        return cls(
            pkg_file=pkg_file,
            pkgName=PkgVer.deserialize(pkg_ver_str),
            pkgOrigin=dct.get('pkgOrigin'),
            paths=utils.ensure_valid_paths(dct['paths']),
            depNames=dct[C.K_DEP_NAMES],
            digest=digest.Digest.deserialize(dct[C.K_DIGEST]),
        )

    def serialize(self):
        """Serialize."""
        pfile = os.path.basename(self.pkg_file)
        return {
            "pkg_file": pfile,
            C.K_PKG_NAME: self.pkgName.serialize(),
            C.K_PKG_ORIGIN: self.pkgOrigin,
            C.K_PATH: self.paths,
            C.K_DEP_NAMES: self.depNames,
            C.K_DIGEST: self.digest.serialize(),
        }

    def __repr__(self):
        return 'PkgDigest{}'.format(self.serialize())


class PkgExport(PkgDigest):
    """Pkg with self.export and depdency's export fields resolved."""

    # pylint: disable=too-many-arguments
    def __init__(self, pkg_file, pkgName, pkgOrigin, paths, depNames, deps, export):
        super(PkgExport, self).__init__(
            pkg_file=pkg_file,
            pkgName=pkgName,
            pkgOrigin=pkgOrigin,
            paths=paths,
            depNames=depNames,
        )

        self.deps = deps
        self.export = export

    @classmethod
    def deserialize(cls, dct, pkg_file):
        dig = PkgDigest.deserialize(dct, pkg_file)
        return cls(
            pkg_file=dig.pkg_file,
            pkgName=dig.pkgName,
            pkgOrigin=dig.pkgOrigin,
            paths=dig.paths,
            depNames=dig.depNames,
            digest=dig.digest,
            deps=dct[C.K_DEPS],
            export=dct[C.K_EXPORT],
        )

    def serialize(self):
        dct = super(PkgExport, self).serialize()
        dct[C.K_DEPS] = self.deps
        dct[C.K_EXPORT] = self.export
        return dct
