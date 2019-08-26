# -*- coding: utf-8 -*-
# ⏾🌊🛠 wake software's true potential
#
# Copyright (C) 2019 Rett Berg <github.com/vitiral>
#
# The source code is Licensed under either of
#
# * Apache License, Version 2.0, ([LICENSE-APACHE](LICENSE-APACHE) or
#   http://www.apache.org/licenses/LICENSE-2.0)
# * MIT license ([LICENSE-MIT](LICENSE-MIT) or
#   http://opensource.org/licenses/MIT)
#
# at your option.
#
# Unless you explicitly state otherwise, any contribution intentionally submitted
# for inclusion in the work by you, as defined in the Apache-2.0 license, shall
# be dual licensed as above, without any additional terms or conditions.

from __future__ import unicode_literals

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
        self.dir = tempfile.mkdtemp(prefix=prefix or '', dir=dir)

    def __enter__(self):
        return self.dir

    def __exit__(self, type, value, traceback):
        self.cleanup()

    def cleanup(self):
        if os.path.exists(self.dir):
            shutil.rmtree(self.dir)
