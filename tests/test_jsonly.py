import unittest
import wake
import os

DIR_TEST = os.path.dirname(os.path.abspath(__file__))
DIR_JSONLY = os.path.join(DIR_TEST, "jsonly")


class TestJsonnetOnly(unittest.TestCase):
    def run_test(self, name):
        directory = os.path.join(DIR_JSONLY, name)

    def test_simple(self):
        pass
