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

from .constants import *
from . import utils
from . import digest


class PkgName(utils.TupleObject):
    def __init__(self, namespace, name):
        self.namespace = namespace
        self.name = name

    def __str__(self):
        return WAKE_SEP.join((self.namespace, self.name))

    def __repr__(self):
        return "name:{}".format(self)

    def _tuple(self):
        return (self.namespace, self.name)


class PkgReq(utils.TupleObject):
    def __init__(self, namespace, name, semver):
        self.namespace = namespace
        self.name = name
        self.semver = semver

    @classmethod
    def deserialize(cls, string):
        split = string.split(WAKE_SEP)
        if len(split) > 3:
            raise ValueError("Must have 3 components split by {}: {}".format(
                WAKE_SEP, string))

        namespace, name, semver = split
        return cls(namespace=namespace, name=name, semver=semver)

    def serialize(self):
        return WAKE_SEP.join(self._tuple())

    def __str__(self):
        return self.serialize()

    def __repr__(self):
        return "req:{}".format(self)

    def _tuple(self):
        return (self.namespace, self.name, self.semver)


class PkgRequest(utils.TupleObject):
    def __init__(self, requestingPkgVer, pkgReq):
        self.requestingPkgVer = requestingPkgVer
        self.pkgReq = pkgReq

    def serialize(self):
        return WAKE_SEP.join((
            self.requestingPkgVer.serialize(),
            self.pkgReq.serialize(),
        ))

    def __str__(self):
        return self.serialize()

    def __repr__(self):
        return "pkgRequest:{}".format(self)

    def _tuple(self):
        return (self.requestingPkgVer, self.pkgReq)


class PkgVer(utils.TupleObject):
    def __init__(self, namespace, name, version, digest):
        self.namespace = namespace
        self.name = name
        self.version = version
        self.digest = digest

    @classmethod
    def deserialize(cls, string):
        split = string.split(WAKE_SEP)
        if len(split) > 4:
            raise ValueError("Must have 4 components split by {}: {}".format(
                WAKE_SEP, string))

        namespace, name, version, digest_str = split
        return cls(
            namespace=namespace,
            name=name,
            version=version,
            digest=digest.Digest.deserialize(digest_str),
        )

    def serialize(self):
        return WAKE_SEP.join((
            self.namespace,
            self.name,
            self.version,
            self.digest.serialize(),
        ))

    def __str__(self):
        return self.serialize()

    def __repr__(self):
        return "ver:{}".format(self)

    def _tuple(self):
        return (self.namespace, self.name, self.version, self.digest)


class PkgDigest(utils.SafeObject):
    """The items which are used in the pkg digest.

    These items must completely define the package for transport and use.
    """
    def __init__(self, pkg_file, pkgVer, pkgOrigin, paths, depsReq):
        if pkg_file not in paths:
            paths.add('./' + FILE_PKG_DEFAULT)

        self.pkg_file = pkg_file
        self.pkg_dir = os.path.dirname(pkg_file)
        self.pkg_digest = os.path.join(self.pkg_dir, DEFAULT_FILE_DIGEST)
        self.pkgVer = pkgVer
        self.pkgOrigin = pkgOrigin
        self.paths = paths
        self.depsReq = depsReq

    @classmethod
    def deserialize(cls, dct, pkg_file):
        pkg_ver_str = utils.ensure_str('pkgVer', dct['pkgVer'])
        return cls(
            pkg_file=pkg_file,
            pkgVer=PkgVer.deserialize(pkg_ver_str),
            pkgOrigin=dct.get('pkgOrigin'),
            paths=set(utils.ensure_valid_paths(dct['paths'])),
            depsReq=dct['depsReq'],
        )

    def serialize(self):
        pdir, pfile = os.path.split(self.pkg_file)
        relpaths = sorted(self.paths)
        return {
            "pkg_file": pfile,
            "pkgVer": self.pkgVer.serialize(),
            "pkgOrigin": self.pkgOrigin,
            "paths": relpaths,
            "depsReq": self.depsReq,
        }

    def __repr__(self):
        return 'PkgDigest{}'.format(self.serialize())


class PkgExport(PkgDigest):
    def __init__(self, pkg_file, pkgVer, pkgOrigin, paths, depsReq, deps,
                 export):
        super(PkgExport, self).__init__(
            pkg_file=pkg_file,
            pkgVer=pkgVer,
            pkgOrigin=pkgOrigin,
            paths=paths,
            depsReq=depsReq,
        )

        self.deps = deps
        self.export = export

    @classmethod
    def deserialize(cls, dct, pkg_file):
        digest = PkgDigest.deserialize(dct, pkg_file)
        return cls(
            pkg_file=digest.pkg_file,
            pkgVer=digest.pkgVer,
            pkgOrigin=digest.pkgOrigin,
            paths=digest.paths,
            depsReq=digest.depsReq,
            deps=dct['deps'],
            export=dct['export'],
        )

    def serialize(self):
        dct = super(PkgExport, self).serialize()
        dct['deps'] = self.deps
        dct['export'] = self.export
        return dct
