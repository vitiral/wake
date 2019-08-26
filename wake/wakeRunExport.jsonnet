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

local wake_noPkgs = (import 'WAKE_LIB');
local pkg_fn = (import 'PKG_FILE');
local pkgsDefined = (import 'PKGS_DEFINED');

local wake =
    wake_noPkgs
    {
        _private+: {
            pkgsDefined: pkgsDefined,
        },
    };

# instantiate and return the root pkg
local pkgInitial = pkg_fn(wake);

local pkgExport = wake._private.recurseCallExport(wake, pkgInitial);

pkgExport
