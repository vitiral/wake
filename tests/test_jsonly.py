import unittest
import wake
import os

import yaml

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
        expected = {
            'pkg_file': 'PKG.libsonnet',
            'pkgVer': 'ver:@simple@0.1.0@md5.0e86e5c6a0b61667eb1f4886eb3a0664',
            'pkgOrigin': None,
            'paths': ['PKG.libsonnet'],
            'deps': {},
        }
        self.run_test('simple', expected)
