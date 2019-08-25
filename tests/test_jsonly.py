import unittest
import os

import yaml
import wake
from wake.constants import *

DIR_TEST = os.path.dirname(os.path.abspath(__file__))
DIR_JSONLY = os.path.join(DIR_TEST, "jsonly")

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
        assert expected == result.serialize(), '[[ In ' + name + ' ]]'

    def test_simple(self):
        self.run_test('simple')

    def test_file_paths(self):
        self.run_test('file_paths')

