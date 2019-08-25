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

# Heavily modified from checksumdir v1.1.5
#
# The MIT License (MIT)
# Copyright (c) 2015 cakepietoast
# https://pypi.org/project/checksumdir/#files
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


def loadPkgDigest(state, pkg_file):
    pkg_dir = os.path.dirname(pkg_file)
    digest_path = os.path.join(pkg_dir, DEFAULT_FILE_DIGEST)
    run_digest_text = utils.format_run_digest(pkg_file)

    state_dir = state.create_temp_dir()
    try:
        # Dump fake `.digest.json`
        utils.jsondumpf(digest_path, Digest.SEP.join(["md5", "fake"]))

        # Put the jsonnet run file in place
        run_digest_path = os.path.join(state_dir.dir, FILE_RUN_DIGEST)
        utils.dumpf(run_digest_path, run_digest_text)

        # Get a pkgDigest with the wrong digest value
        pkgDigest = pkg.PkgDigest.deserialize(
            utils.manifest_jsonnet(run_digest_path),
            pkg_file=pkg_file,
        )

        # Dump real `.digest.json`
        digest = calc_digest(pkgDigest)
        utils.jsondumpf(digest_path, digest.serialize())

        pkgDigest = pkg.PkgDigest.deserialize(
            utils.manifest_jsonnet(run_digest_path),
            pkg_file=pkg_file,
        )

        assert pkgDigest.pkgVer.digest == digest
        return pkgDigest
    finally:
        if os.path.exists(digest_path):
            os.remove(digest_path)
        state_dir.cleanup()


def calc_digest(pkgDigest):
    """Calculate the actual hash from a pkgDigest object."""
    builder = DigestBuilder(pkg_dir=os.path.dirname(pkgDigest.pkg_file))
    builder.update_paths(utils.joinpaths(builder.pkg_dir, pkgDigest.paths))
    return builder.build()


class Digest(utils.TupleObject):
    """The data representation of a digest."""
    SEP = '.'

    def __init__(self, digest, digest_type):
        self.digest = digest
        if digest_type not in DIGEST_TYPES:
            raise ValueError("digest_type must be one of: {}".format(list(DIGEST_TYPES.keys())))
        self.digest_type = digest_type

    def _tuple(self):
        return (self.digest_type, self.digest)

    def __repr__(self):
        return self.SEP.join(self.digest_type, self.digest)

    @classmethod
    def deserialize(cls, string):
        digest_type, digest = string.split(cls.SEP, 1)
        return cls(
            digest=digest,
            digest_type=digest_type,
        )

    def serialize(self):
        return self.SEP.join(self._tuple())

    def __repr__(self):
        return self.serialize()



class DigestBuilder(utils.SafeObject):
    def __init__(self, pkg_dir, digest_type='md5'):
        assert os.path.isabs(pkg_dir)
        if digest_type not in DIGEST_TYPES:
            raise NotImplementedError('Hasher {} not implemented.'.format(digest_type))

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
                fpath = pjoin(root, f)
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
