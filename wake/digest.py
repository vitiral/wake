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
####################################
# Based on a heavily modified snapshot of checksumdir v1.1.5
#
# The MIT License (MIT)
# Copyright (c) 2015 cakepietoast
# https://pypi.org/project/checksumdir/#files
"""Calaculate the hash digest of a package or module."""

import os
import hashlib

from .constants import *
from . import utils
from . import pkg

DIGEST_TYPES = {
    'md5': hashlib.md5,
    'sha1': hashlib.sha1,
    'sha256': hashlib.sha256,
    'sha512': hashlib.sha512
}


def calc_digest(pkgDigest):
    """Calculate the actual hash from a loaded pkgDigest object."""
    builder = DigestBuilder(pkg_dir=os.path.dirname(pkgDigest.pkg_file))
    builder.update_paths(utils.joinpaths(builder.pkg_dir, pkgDigest.paths))
    return builder.build()


class Digest(utils.TupleObject):
    """Serializable digest."""
    SEP = '.'

    def __init__(self, digest, digest_type):
        self.digest = digest
        if digest_type not in DIGEST_TYPES:
            raise ValueError("digest_type must be one of: {}".format(
                list(DIGEST_TYPES.keys())))
        self.digest_type = digest_type

    @classmethod
    def deserialize(cls, string):
        digest_type, digest = string.split(cls.SEP, 1)
        return cls(
            digest=digest,
            digest_type=digest_type,
        )

    @classmethod
    def fake(cls):
        return cls(
            digest='THIS-IS-FAKE',
            digest_type='md5',
        )

    def serialize(self):
        return self.SEP.join(self._tuple())

    def _tuple(self):
        return (self.digest_type, self.digest)

    def __repr__(self):
        return self.SEP.join(self.digest_type, self.digest)

    def __repr__(self):
        return self.serialize()


class DigestBuilder(utils.SafeObject):
    """Build a digest from input files and directories."""
    def __init__(self, pkg_dir, digest_type='md5'):
        assert os.path.isabs(pkg_dir)
        if digest_type not in DIGEST_TYPES:
            raise NotImplementedError(
                'Hasher {} not implemented.'.format(digest_type))

        self.pkg_dir = pkg_dir
        self.digest_type = digest_type
        self.hash_func = DIGEST_TYPES[digest_type]
        self.hashmap = {}
        self.visited = set()

    def update_paths(self, paths):
        paths = sorted(paths)
        for p in paths:
            if os.path.isdir(p):
                self.update_dir(p)
            else:
                self.update_file(p)

    def update_dir(self, dirpath):
        assert os.path.isabs(dirpath), dirpath

        hash_func = self.hash_func
        hashmap = self.hashmap
        visited = self.visited

        if not os.path.isdir(dirpath):
            raise TypeError('{} is not a directory.'.format(dirpath))

        walking = os.walk(dirpath, topdown=True, followlinks=True)
        for root, _walking, files in walking:
            for f in files:
                fpath = os.path.join(root, f)
                if fpath in visited:
                    raise RuntimeError(
                        "Error: infinite directory recursion detected at {}".
                        format(fpath))
                self.update_file(fpath)

        return hashmap

    def update_file(self, fpath):
        assert os.path.isabs(fpath)
        if fpath in self.visited:
            return
        self.visited.add(fpath)
        hasher = self.hash_func()
        blocksize = 64 * 1024
        with open(fpath, 'rb') as fp:
            while True:
                data = fp.read(blocksize)
                if not data:
                    break
                hasher.update(data)
        pkey = os.path.relpath(fpath, self.pkg_dir)
        self.hashmap[pkey] = hasher.hexdigest()

    def reduce(self):
        hashmap = self.hashmap
        hasher = self.hash_func()
        for fpath in sorted(hashmap.keys()):
            hasher.update(fpath.encode())
            hasher.update(hashmap[fpath].encode())
        return hasher.hexdigest()

    def build(self):
        return Digest(digest=self.reduce(), digest_type=self.digest_type)
