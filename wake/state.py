import shutil
import tempfile
import os

from . import utils


class State(object):
    """Stores state on the filesystem for the purpose of loading jsonnet, etc.

    This is used extensively by multiple functions.
    """
    def __init__(self):
        self.temp_dir = TempDir(prefix="wake-")
        self.dir = self.temp_dir.dir

    def create_temp_dir(self, prefix=None):
        return TempDir(prefix=prefix, dir=self.dir)

    def cleanup(self):
        self.temp_dir.cleanup()


class TempDir(utils.SafeObject):
    def __init__(self, prefix=None, dir=None):
        self.dir = tempfile.mkdtemp(prefix=prefix, dir=dir)

    def __enter__(self):
        return self.dir

    def __exit__(self, type, value, traceback):
        self.cleanup()

    def cleanup(self):
        if os.path.exists(self.dir):
            shutil.rmtree(self.dir)
