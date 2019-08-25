import shutil
import tempfile

from . import utils


class State(object):
    """Stores state on the filesystem for the purpose of loading jsonnet, etc.

    This is used extensively by multiple functions.
    """
    def __init__(self):
        self.temp_dir = TempDir(prefix="wake-")
        self.dir = self.temp_dir.dir

    def create_temp_dir(self, prefix=None):
        return tempfile.mkdtemp(prefix=prefix, dir=self.tempdir)

    def clean(self):
        self.temp_dir.clean()


class TempDir(utils.SafeObject):
    def __init__(prefix=None, dir=None):
        self.dir = tempfile.mkdtemp(prefix=prefix, dir=dir)

    def __enter__(self):
        return self.dir

    def __exit__(self, type, value, traceback):
        self.clean()

    def clean(self):
        if os.path.exists(self.tempdir):
            shutil.rmtree(self.tempdir)
