import unittest
import os

import yaml
import wake
from wake.constants import *

DIR_TEST = os.path.dirname(os.path.abspath(__file__))
DIR_JSONLY = os.path.join(DIR_TEST, "jsonly")

DIR_EXAMPLE_DEPS = os.path.join(DIR_JSONLY, "exampleDeps")


def load_yaml(path):
    with open(path) as fd:
        return yaml.safe_load(fd)


class TestJsonnetOnly(unittest.TestCase):
    def setUp(self):
        self.state = wake.state.State()
        self.store = wake.store.Store()

    def tearDown(self):
        self.state.cleanup()

    def run_test(self, name, with_deps=None):
        with_deps = with_deps or []
        for dep in with_deps:
            pkgDigest = os.path.join(DIR_EXAMPLE_DEPS, dep, FILE_PKG_DEFAULT)
            self.store.create_pkg(pkgDigest)

        directory = os.path.join(DIR_JSONLY, name)
        pkgFile = os.path.join(directory, FILE_PKG_DEFAULT)
        pkgDigest = wake.load.loadPkgDigest(
            self.state,
            pkgFile,
            calc_digest=True,
        )
        expected = load_yaml(os.path.join(directory, "expected.yml"))
        assert expected == pkgDigest.serialize(), '[[ digest ' + name + ' ]]'

        export_path = os.path.join(directory, "expectedExport.yml")
        if os.path.exists(export_path):
            expected = load_yaml(export_path)
            result = wake.load.loadPkgExport(
                self.state,
                self.store.storeMap,
                pkgDigest,
            )
            assert expected == result, '[[ export ' + name + ' ]]'

    def test_simple(self):
        self.run_test('simple')

    def test_file_paths(self):
        self.run_test('file_paths')

    def test_dir_paths(self):
        self.run_test('dir_paths')

    def test_simple_fake_deps(self):
        self.run_test('simple-fake_deps')
