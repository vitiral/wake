#!/usr/bin/python3

from wakedev import *
from wakepkg import *


def create_defined_pkgs(pkgs_defined):
    out = ["{"]

    # TODO: write jsonnet

    out.append("}")
    return "\n".join(out)




class Config(object):
    def __init__(self):
        self.user_path = abspath(os.getenv("WAKEPATH", "~/.wake"))
        self.base = os.getcwd()

        self.pkg_config = PkgConfig(self.base)

        user_file = pjoin(self.user_path, "user.jsonnet")
        if not path.exists(user_file):
            fail("must instantiate user credentials: " + user_file)
        self.user = manifest_jsonnet(user_file)

        self.store = pjoin(self.user_path, self.user.get('store', 'store'))
        self.cache_defined = pjoin(self.store, "pkgsDefined")
        self.cache_pkgs = pjoin(self.store, "pkgs")

    def init_cache(self):
        os.makedirs(self.cache_defined, exist_ok=True)
        os.makedirs(self.cache_pkgs, exist_ok=True)

    def remove_cache(self):
        self.pkg_config.remove_pkg_wake()
        rmtree(self.cache_defined)
        rmtree(self.cache_pkgs)

    def handle_unresolved_pkg(self, pkg):
        from_ = pkg['from']
        if not isinstance(from_, str):
            raise NotYetImplementedError()

        assert_valid_path(from_)
        pkg_config = PkgConfig(from_)
        root = pkg_config.compute_root()
        pcache = pjoin(self.cache_pkgs, root.pkgId)

        meta = pkg_config.get_current_meta()
        computed = pkg_config.compute_pkg_meta()

        if os.path.exists(pcache):
            # TODO: validate metadata or something
            pass
        else:
            assert path.exists(self.cache_pkgs), self.cache_pkgs
            os.mkdir(pcache)


## Helpers

# Heavily modified from checksumdir v1.1.5
# The MIT License (MIT)
# Copyright (c) 2015 cakepietoast
# https://pypi.org/project/checksumdir/#files

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
        meta = config.get_current_meta()
        if meta is None:
            fail("{} meta file must exist".format(config.pkg_meta))
        return cls(config.base, hash_type=meta[F_HASHTYPE])

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


## COMMANDS AND MAIN

def build(args):
    config = Config()
    print("## building local pkg {}".format(config.base))
    pkg_config = config.pkg_config

    print("-> initializing the global cache")
    if MODE == DEBUG:
        config.remove_cache()
    config.init_cache()

    print("-> recomputing PKG.meta")
    pkg_config.dump_pkg_meta()

    print("-> Starting build cycles")
    pkg_config.init_pkg_wake()
    cycle = 0
    while True:
        manifest = pkg_config.manifest_pkg()
        pkgs = manifest['all']

        num_unresolved = 0
        for pkg in pkgs:
            assert is_pkg(pkg)
            if is_unresolved(pkg):
                num_unresolved += 1
                config.handle_unresolved_pkg(pkg)

        break


    print("## MANIFEST")
    pp(pkg_config.manifest_pkg())


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description='Wake: the pkg manager and build system of the web',
    )

    subparsers = parser.add_subparsers(help='[sub-command] help')
    parser_build = subparsers.add_parser(
        'build',
        help='build the pkg in the current directory'
    )
    parser_build.set_defaults(func=build)

    return parser.parse_args(argv)

def main(argv):
    args = parse_args(argv[1:])

    print(args)
    args.func(args)


if __name__ == '__main__':
    print(sys.argv)
    main(sys.argv)
