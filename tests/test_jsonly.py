import unittest
import wake
import os

from wake.constants import *

DIR_TEST = os.path.dirname(os.path.abspath(__file__))
DIR_JSONLY = os.path.join(DIR_TEST, "jsonly")


class TestJsonnetOnly(unittest.TestCase):
    def setUp(self):
        self.state = wake.state.State()

    def tearDown(self):
        self.state.cleanup()

    def run_test(self, name):
        directory = os.path.join(DIR_JSONLY, name)
        pkgFile = os.path.join(directory, DEFAULT_PKG_LIBSONNET)
        pkgDigest = wake.digest.loadPkgDigest(self.state, pkgFile)
        assert False, "not done"

    def test_simple(self):
        self.run_test('simple')
