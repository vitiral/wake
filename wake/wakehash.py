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

# Heavily modified from checksumdir v1.1.5
#
# The MIT License (MIT)
# Copyright (c) 2015 cakepietoast
# https://pypi.org/project/checksumdir/#files

from .utils import *

class HashStuff(object):
    HASH_TYPES = {
        'md5': hashlib.md5,
        'sha1': hashlib.sha1,
        'sha256': hashlib.sha256,
        'sha512': hashlib.sha512
    }

    def __init__(self, base, hash_type='md5'):
        assert path.isabs(base)

        self.base = base
        self.hash_type = hash_type
        self.hash_func = self.HASH_TYPES[hash_type]
        if not self.hash_func:
            raise NotImplementedError('{} not implemented.'.format(hash_type))
        self.hashmap = {}
        self.visited = set()

    @classmethod
    def from_config(cls, config):
        fingerprint = config.get_current_fingerprint()
        if fingerprint is None:
            fail("{} fingerprint file must exist".format(config.pkg_fingerprint))
        return cls(config.base, hash_type=fingerprint[F_HASHTYPE])

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

        for root, dirs, files in os.walk(dirpath, topdown=True, followlinks=True):
            for f in files:
                fpath = pjoin(root, f)
                if fpath in visited:
                    raise RuntimeError(
                        "Error: infinite directory recursion detected at {}"
                        .format(fpath)
                    )
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

