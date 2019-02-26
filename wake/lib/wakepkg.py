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

from wakedev import *
from wakehash import *


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
                PkgUnresolved.from_dict(p) if is_unresolved(p)
                else PkgSimple.from_dict(p)
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
        return cls(
            hash_=dct['hash'],
            hash_type=dct['hash_type']
        )

    def to_dict(self):
        return {
            'hash': self.hash,
            'hashType': self.hash_type,
        }


class PkgSimple(object):
    """Pull out only the data we care about."""
    def __init__(self, state, pkg_id, name, version, namespace, fingerprint, paths, def_paths):
        hash_ = fingerprint['hash']
        expected_pkg_id = [name, version, namespace, hash_]
        assert expected_pkg_id == pkg_id.split(','), (
            "pkgId != 'name,version,namespace,hash':\n{}\n{}".format(
                pkg_id, expected_pkg_id))

        assert_valid_paths(paths)
        assert_valid_paths(def_paths)

        self.state = state
        self.pkg_root = path.join("./", FILE_PKG)
        self.pkg_local_deps = path.join("./", DIR_WAKE, FILE_LOCAL_DEPS)
        self.pkg_id = pkg_id
        self.name = name
        self.namespace = namespace
        self.fingerprint = fingerprint

        self.paths = paths
        self.def_paths = def_paths

    @classmethod
    def from_dict(cls, dct):
        assert is_pkg(dct)
        assert not is_unresolved(dct), "unresolved pkg: " + repr(dct)

        return cls(
            state=dct[F_STATE],
            pkg_id=dct['pkgId'],
            name=dct['name'],
            version=dct['version'],
            namespace=dct['namespace'],
            fingerprint=dct['fingerprint'],
            paths=dct['paths'],
            def_paths=dct['defPaths'],
        )

    def to_dict(self):
        # TODO: probably want all, only a few is good for repr for now
        return {
            F_STATE: self.state,
            'pkgId': self.pkg_id,
            'paths': self.paths,
            'defPaths': self.def_paths,
        }

    def get_def_fsentries(self):
        """Return all defined pkgs, including root."""
        default = [self.pkg_root, self.pkg_local_deps]
        return itertools.chain(default, self.def_paths)

    def get_fsentries(self):
        return itertools.chain(self.get_def_fsentries(), self.paths)

    def get_pkg_req(self):
        """Convert to just the pkg req key (no hash)."""

    def is_unresolved(self):
        return False


class PkgUnresolved(object):
    def __init__(self, pkg_req, from_):
        if isinstance(from_, str) and not from_.startswith('./'):
            raise TypeError(
                "{}: from must start with ./ for local pkgs: {}"
                .format(pkg_req, from_))
        self.pkg_req = pkg_req
        self.from_ = from_

    @classmethod
    def from_dict(cls, dct):
        assert is_pkg(dct)
        assert is_unresolved(dct)

        return cls(
            pkg_req=dct['pkgReq'],
            from_=dct['from'],
        )

    def to_dict(self):
        return {
            F_STATE: S_UNRESOLVED,
            'pkgReq': self.pkg_req,
            'from': self.from_,
        }

    def is_unresolved(self):
        return True

    def is_from_local(self):
        return isinstance(self.from_, str)

class PkgConfig(object):
    def __init__(self, base):
        self.base = abspath(base)
        self.pkg_root = pjoin(self.base, "PKG.libsonnet")
        self.wakedir = pjoin(self.base, ".wake")
        self.pkg_fingerprint = pjoin(self.wakedir, FILE_FINGERPRINT)
        self.path_local_deps = pjoin(self.wakedir, FILE_LOCAL_DEPS)
        self.pkgs_local_lib = pjoin(self.wakedir, FILE_PKGS_LOCAL_LIB)

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

    def assert_fingerprint_matches(self, pkgSimple, check_against=None):
        """Assert that the defined fingerprints all match.
        """
        fingerprint = self.get_current_fingerprint()
        computed = self.compute_pkg_fingerprint()
        assert fingerprint == computed, "own fingerprint does not match."

        if check_against is not None:
            assert fingerprint == check_against

    def __repr__(self):
        return "PkgConfig({})".format(self.base)
