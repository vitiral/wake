import unittest
import os

import yaml
import wake
from wake.constants import *

DIR_TEST = os.path.dirname(os.path.abspath(__file__))
DIR_JSONLY = os.path.join(DIR_TEST, "jsonly")

# ./fakeStore/{libA}/PKG.jsonnet
DIR_FAKE_STORE = os.path.join(DIR_JSONLY, "fakeStore")
KEY_LIBA = WAKE_SEP.join([
    "",
    "file_paths",
    "0.1.0",
    "md5.fake-digest",
    "fake",
    "libA",
    ">=5.2.0",
])
DIR_LIBA = os.path.join(DIR_FAKE_STORE, KEY_LIBA)
PKG_LIBA = os.path.join(DIR_LIBA, DEFAULT_PKG_LIBSONNET)

STORE_MAP = {KEY_LIBA: PKG_LIBA}


def load_yaml(path):
    with open(path) as fd:
        return yaml.safe_load(fd)


class TestJsonnetOnly(unittest.TestCase):
    def setUp(self):
        self.state = wake.state.State()

    def tearDown(self):
        self.state.cleanup()

    def run_test(self, name):
        directory = os.path.join(DIR_JSONLY, name)
        pkgFile = os.path.join(directory, DEFAULT_PKG_LIBSONNET)
        result = wake.load.loadPkgDigest(self.state, pkgFile)
        expected = load_yaml(os.path.join(directory, "expected.yml"))
        assert expected == result.serialize(), '[[ digest ' + name + ' ]]'

        export_path = load_yaml(os.path.join(directory, "expectedExport.yml"))
        if os.path.exists(export_path):
            expected = load_yaml(export_path)
            result = wake.load.loadPkgExport(self.state, STORE_MAP, pkgFile)
            assert expected == result, '[[ export ' + name + ' ]]'

    def test_simple(self):
        self.run_test('simple')

    def test_file_paths(self):
        self.run_test('file_paths')

    def test_dir_paths(self):
        self.run_test('dir_paths')

    def test_simple_fake_deps(self):
        self.run_test('simple-fake_deps')
