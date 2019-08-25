import os

from .constants import *


def setup_root(root_file):
    directory = os.path.dirname(os.path.abspath(root_file))
    pkg_libsonnet = os.path.join(directory, DEFAULT_PKG_LIBSONNET)
