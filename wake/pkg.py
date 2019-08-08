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

from .utils import *


class PkgConfig(object):
    def __init__(self, base):
        self.base = abspath(base)
        self.pkg_root = pjoin(self.base, FILE_PKG)
        self.wakedir = pjoin(self.base, ".wake")
        self.pkg_fingerprint = pjoin(self.wakedir, FILE_FINGERPRINT)
        self.path_local_deps = pjoin(self.wakedir, FILE_LOCAL_DEPENDENCIES)

    def init_wakedir(self):
        assert path.exists(self.base)
        assert path.exists(self.pkg_root)
        os.makedirs(self.wakedir, exist_ok=True)

    def get_current_fingerprint(self):
        if not path.exists(self.pkg_fingerprint):
            return None
        return jsonloadf(self.pkg_fingerprint)

    def path_abs(self, relpath):
        return pjoin(self.base, relpath)

    def paths_abs(self, relpaths):
        return map(self.path_abs, relpaths)

    def __repr__(self):
        return "PkgConfig({})".format(self.base)


class PkgKey(object):
    def __init__(self, namespace, name):
        self.namespace = namespace
        self.name = name

    def __hash__(self):
        return hash((self.namespace, self.name))

    def __str__(self):
        return WAKE_SEP.join((self.namespace, self.name))

    def __repr__(self):
        return "PkgKey({})".format(self)


class PkgReq(object):
    def __init__(self, namespace, name, version, hash_=None):
        self.namespace = namespace
        self.name = name
        self.version = version
        self.hash = hash_

    @classmethod
    def from_str(cls, s):
        spl = s.split(WAKE_SEP)
        namespace, name, version = spl[:3]
        if len(spl) > 4:
            raise ValueError(s)
        elif len(spl) == 4:
            hash_ = spl[3]
        else:
            hash_ = None

        return cls(namespace, name, version, hash_)

    def __str__(self):
        out = [
            self.namespace,
            self.name,
            self.version,
        ]
        if self.hash:
            out.append(self.hash)
        return WAKE_SEP.join(out)

    def __repr__(self):
        return "PkgReq({})".format(self)


class PkgManifest(object):
    """The result of "running" a pkg."""
    def __init__(self, root, all_pkgs):
        self.root = root
        self.all = all_pkgs

    @classmethod
    def from_dict(cls, dct):
        return cls(
            root=PkgSimple.from_dict(dct['root']),
            all_pkgs=[
                PkgUnresolved.from_dict(p)
                if is_unresolved(p) else PkgSimple.from_dict(p)
                for p in dct['all']
            ],
        )

    def to_dict(self):
        return {
            "root": self.root.to_dict(),
            "all": [p.to_dict() for p in self.all],
        }


class Fingerprint(object):
    def __init__(self, hash_, hash_type):
        self.hash = hash_
        self.hash_type = hash_type

    @classmethod
    def from_dict(cls, dct):
        return cls(hash_=dct['hash'], hash_type=dct['hash_type'])

    def to_dict(self):
        return {
            'hash': self.hash,
            'hashType': self.hash_type,
        }


class PkgSimple(object):
    """Pull out only the data we care about."""
    def __init__(self, state, pkg_id, namespace, name, version, description,
                 fingerprint, pkgs, paths, paths_def, exports):
        hash_ = fingerprint['hash']
        expected_pkg_id = [namespace, name, version, hash_]
        assert expected_pkg_id == pkg_id.split(WAKE_SEP), (
            "pkgVer != 'namespace#name#version#hash':\n{}\n{}".format(
                pkg_id, expected_pkg_id))

        invalid_paths = []
        for p in itertools.chain(paths, paths_def):
            try:
                assert_valid_path(p)
                assert_not_wake(p)
            except ValueError as e:
                invalid_paths.append("{}: {}".format(p, e))

        if invalid_paths:
            raise ValueError("{} has Invalid paths:\n{}".format(
                pkg_id, "\n".join(invalid_paths)))

        self.state = state
        self.pkg_root = path.join("./", FILE_PKG)
        self.pkg_local_deps = path.join("./", DIR_WAKE,
                                        FILE_LOCAL_DEPENDENCIES)
        self.pkg_fingerprint = path.join("./", DIR_WAKE, FILE_FINGERPRINT)
        # TODO: pkg_id_str and pkg_id
        self.pkg_id = pkg_id
        self.namespace = namespace
        self.name = name
        self.version = version
        self.description = description
        self.fingerprint = fingerprint
        self.pkgs = pkgs

        self.paths = paths
        self.paths_def = paths_def
        self.exports = exports

    def get_pkg_key(self):
        return PkgKey(self.namespace, self.name)

    def __repr__(self):
        return "{}(id={}, state={})".format(self.__class__.__name__,
                                            self.pkg_id, self.state)

    @classmethod
    def from_dict(cls, dct):
        assert is_pkg(dct)
        assert not is_unresolved(dct), "unresolved pkg: " + repr(dct)

        return cls(
            state=dct[F_STATE],
            pkg_id=dct['pkgVer'],
            namespace=dct['namespace'],
            name=dct['name'],
            version=dct['version'],
            description=dct['description'],
            fingerprint=dct['fingerprint'],
            pkgs=dct['pkgs'],
            paths=dct['paths'],
            paths_def=dct['pathsDef'],
            exports=dct['exports'],
        )

    def to_dict(self):
        # TODO: probably want all, only a few is good for repr for now
        return {
            F_STATE: self.state,
            'pkgVer': self.pkg_id,
            'paths': self.paths,
            'pathsDef': self.paths_def,
            'exports': self.exports,
            'pkgs': self.pkgs,
        }

    def get_def_fsentries(self):
        """Return all defined pkgs, including root."""
        default = [
            self.pkg_root,
            self.pkg_local_deps,
            self.pkg_fingerprint,
        ]
        return itertools.chain(default, self.paths_def)

    def get_fsentries(self):
        return itertools.chain(self.get_def_fsentries(), self.paths)

    def is_unresolved(self):
        return False

    def get_local_deps(self):
        if path.exists(self.pkg_local_deps):
            return jsonloadf(self.pkg_local_deps)
        else:
            return None


class PkgUnresolved(object):
    def __init__(self, pkg_req, from_, using_pkg, full, exec_):
        if isinstance(from_, str) and not from_.startswith('./'):
            raise TypeError(
                "{}: from must start with ./ for local pkgs: {}".format(
                    pkg_req, from_))
        if isinstance(pkg_req, str):
            pkg_req = PkgReq.from_str(pkg_req)
        self.pkg_req = pkg_req
        self.from_ = from_
        self.using_pkg = using_pkg
        self.full = full
        self.exec_ = exec_

    @classmethod
    def from_dict(cls, dct):
        assert is_pkg(dct)
        assert is_unresolved(dct)

        exec_ = dct['exec']
        if exec_ is not None:
            exec_ = Exec.from_dict(exec_)

        return cls(
            pkg_req=dct['pkgReq'],
            from_=dct['from'],
            using_pkg=dct['usingPkg'],
            full=dct,
            exec_=exec_,
        )

    def to_dict(self):
        return {
            F_STATE: S_UNRESOLVED,
            'pkgReq': self.pkg_req,
            'from': self.from_,
            'usingPkg': self.using_pkg,
        }

    def is_unresolved(self):
        return True

    def is_from_local(self):
        return self.using_pkg == None


class Exec(object):
    def __init__(self, path_ref, container, config, args, env):
        self.path_ref = path_ref
        self.container = container
        self.config = config
        self.args = args
        self.env = env

    @classmethod
    def from_dict(cls, dct):
        container = dct['container']
        if isinstance(container, dict):
            container = Exec.from_dict(container)

        return cls(
            path_ref=PathRefPkg.from_dict(dct['pathRef']),
            container=container,
            config=dct['config'],
            args=dct['args'],
            env=dct['env'],
        )


class PathRefPkg(object):
    def __init__(self, pkg_id, path):
        self.pkg_id = pkg_id
        self.path = path

    @classmethod
    def from_dict(cls, dct):
        return cls(
            pkg_id=dct['pkgVer'],
            path=dct['path'],
        )
