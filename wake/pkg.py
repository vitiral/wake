from .constants import *
from . import utils


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
    def from_str(cls, s):
        spl = s.split(WAKE_SEP)
        if len(spl) > 3:
            raise ValueError("Must have 3 components split by {}: {}".format(
                WAKE_SEP, s))

        namespace, name, semver = spl
        return cls(namespace=namespace, name=name, semver=semver)

    def __str__(self):
        return WAKE_SEP.join(self._tuple())

    def __repr__(self):
        return "req:{}".format(self)

    def _tuple(self):
        return (self.namespace, self.name, self.semver)


class PkgVer(utils.TupleObject):
    def __init__(self, namespace, name, version, diget):
        self.namespace = namespace
        self.name = name
        self.version = version
        self.digest = digest

    @classmethod
    def from_str(cls, s):
        spl = s.split(WAKE_SEP)
        if len(spl) > 4:
            raise ValueError("Must have 4 components split by {}: {}".format(
                WAKE_SEP, s))

        namespace, name, version, digest = spl
        return cls(
            namespace=namespace,
            name=name,
            version=version,
            digest=digest,
        )

    def __str__(self):
        return WAKE_SEP.join(self._tuple())

    def __repr__(self):
        return "ver:{}".format(self)

    def _tuple(self):
        return (self.namespace, self.name, self.version, digest)


class PkgDigest(utils.SafeObject):
    """The items which are used in the pkg digest.

    These items must completely define the package for transport and use.
    """
    def __init__(self, pkg_file, pkgVer, pkgOrigin, paths, deps):
        if pkg_file not in paths:
            paths.add(pkg_file)

        self.pkg_file = pkg_file
        self.pkgVer = pkgVer
        self.pkgOrigin = pkgOrigin
        self.paths = paths
        self.deps = deps


    @classmethod
    def from_dict(cls, dct, pkg_file):
        return cls(
            pkg_file=pkg_file,
            pkgVer=utils.ensure_str('pkgVer', dct['pkgVer']),
            pkgOrigin=dct.get('pkgOrigin'),
            paths=set(utils.ensure_valid_paths(dct['paths'])),
            deps=dct['deps'],
        )
