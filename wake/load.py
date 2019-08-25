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
"""Load packages in various states."""

import os
import hashlib

from .constants import *
from . import utils
from . import pkg
from . import digest


def loadPkgDigest(state, pkg_file):
    """Load a package digest, returning PkgDigest.

    Note: The `state` is used to create a temporary directory for storing the
    custom-created jsonnet running script.
    """
    pkg_dir = os.path.dirname(pkg_file)
    digest_path = os.path.join(pkg_dir, DEFAULT_FILE_DIGEST)
    run_digest_text = utils.format_run_digest(pkg_file)

    state_dir = state.create_temp_dir()
    try:
        # Dump fake `.digest.json`
        utils.jsondumpf(digest_path, digest.Digest.fake().serialize())

        # Put the jsonnet run file in place
        run_digest_path = os.path.join(state_dir.dir, FILE_RUN_DIGEST)
        utils.dumpf(run_digest_path, run_digest_text)

        # Get a pkgDigest with the wrong digest value
        pkgDigest = pkg.PkgDigest.deserialize(
            utils.manifest_jsonnet(run_digest_path),
            pkg_file=pkg_file,
        )

        # Dump real `.digest.json`
        digest_value = digest.calc_digest(pkgDigest)
        utils.jsondumpf(digest_path, digest_value.serialize())

        pkgDigest = pkg.PkgDigest.deserialize(
            utils.manifest_jsonnet(run_digest_path),
            pkg_file=pkg_file,
        )

        assert pkgDigest.pkgVer.digest == digest_value
        return pkgDigest
    finally:
        if os.path.exists(digest_path):
            os.remove(digest_path)
        state_dir.cleanup()
