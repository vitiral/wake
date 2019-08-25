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

from .utils import *

def loadPkgDigest(root_file):
    pass


class Digest(object):
    DIGEST_TYPES = {
        'md5': hashlib.md5,
        'sha1': hashlib.sha1,
        'sha256': hashlib.sha256,
        'sha512': hashlib.sha512
    }

    def __init__(self, base, hash_type='md5'):
        assert path.isabs(base)

        self.base = base
        self.hash_type = hash_type
        self.hash_func = self.DIGEST_TYPES[hash_type]
        if not self.hash_func:
            raise NotImplementedError('{} not implemented.'.format(hash_type))
        self.hashmap = {}
        self.visited = set()

    @classmethod
    def from_config(cls, config):
        digest = config.get_current_digest()
        if digest is None:
            fail("{} digest file must exist".format(config.pkg_digest))
        return cls(config.base, hash_type=digest[F_DIGESTTYPE])

    def update_paths(self, paths):
        for p in paths:
            if path.isdir(p):
                self.update_dir(p)
            else:
                self.update_file(p)

    def update_dir(self, dirpath):
        assert path.isabs(dirpath), dirpath

        hash_func = self.hash_func
        hashmap = self.hashmap
        visited = self.visited

        if not os.path.isdir(dirpath):
            raise TypeError('{} is not a directory.'.format(dirpath))

        for root, dirs, files in os.walk(dirpath,
                                         topdown=True,
                                         followlinks=True):
            for f in files:
                fpath = pjoin(root, f)
                if fpath in visited:
                    raise RuntimeError(
                        "Error: infinite directory recursion detected at {}".
                        format(fpath))
                visited.add(fpath)
                self.update_file(fpath)

        return hashmap

    def update_file(self, fpath):
        assert path.isabs(fpath)
        hasher = self.hash_func()
        blocksize = 64 * 1024
        with open(fpath, 'rb') as fp:
            while True:
                data = fp.read(blocksize)
                if not data:
                    break
                hasher.update(data)
        pkey = path.relpath(fpath, self.base)
        self.hashmap[pkey] = hasher.hexdigest()

    def reduce(self):
        hashmap = self.hashmap
        hasher = self.hash_func()
        for fpath in sorted(hashmap.keys()):
            hasher.update(fpath.encode())
            hasher.update(hashmap[fpath].encode())
        return hasher.hexdigest()
