import unittest
import os

import yaml
import wake
from wake.constants import *

DIR_TEST = os.path.dirname(os.path.abspath(__file__))
DIR_JSONLY = os.path.join(DIR_TEST, "jsonly")

DIR_EXAMPLE_DEPS = os.path.join(DIR_JSONLY, "exampleDeps")
PKG_LIBA = os.path.join(DIR_EXAMPLE_DEPS, "libA-5.5.0", FILE_PKG_DEFAULT)


def load_yaml(path):
    with open(path) as fd:
        return yaml.safe_load(fd)


class TestJsonnetOnly(unittest.TestCase):
    def setUp(self):
        self.state = wake.state.State()
        self.store = wake.store.Store(self.state)

        libA_pkgDigest = wake.load.loadPkgDigest(self.state,
                                                 PKG_LIBA,
                                                 calc_digest=True)
        self.libA_pkgDigest = self.store.create_pkg(libA_pkgDigest)

    def tearDown(self):
        # self.state.cleanup()
        pass

    def run_test(self, name, create_pkgs_defined=None):

        directory = os.path.join(DIR_JSONLY, name)
        pkgFile = os.path.join(directory, FILE_PKG_DEFAULT)
        pkgDigest = wake.load.loadPkgDigest(
            self.state,
            pkgFile,
            calc_digest=True,
        )
        expected = load_yaml(os.path.join(directory, "expected.yml"))
        # assert expected == pkgDigest.serialize(), '[[ digest ' + name + ' ]]'

        export_path = os.path.join(directory, "expectedExport.yml")
        if os.path.exists(export_path):
            if create_pkgs_defined:
                pkgsDefined = create_pkgs_defined(pkgDigest)
            else:
                pkgsDefined = {}

            expected = load_yaml(export_path)
            result = wake.load.loadPkgExport(
                self.state,
                pkgsDefined=pkgsDefined,
                pkgDigest=pkgDigest,
            )
            assert expected == result, '[[ export ' + name + ' ]]'

    def test_simple(self):
        self.run_test('simple')

    def test_file_paths(self):
        self.run_test('file_paths')

    def test_dir_paths(self):
        self.run_test('dir_paths')

    def test_simple_fake_deps(self):
        def create_pkgs_defined(pkgDigest):
            libA_request = wake.pkg.PkgRequest(
                pkgDigest.pkgVer,
                wake.pkg.PkgReq("fake", "libA", ">=5.2.0"),
            )

            return {
                libA_request.serialize(): self.libA_pkgDigest.pkg_file,
            }

        self.run_test('simple-fake_deps',
                      create_pkgs_defined=create_pkgs_defined)
