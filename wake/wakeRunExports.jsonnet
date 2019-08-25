local wakelib = import "WAKELIB";
# local pkgsDefined = import "PKGS_DEFINED";

local wake =
    wakelib
    + {
        _private+: {
            # pkgsDefined: pkgsDefined,
        },
    };

// instantiate and return the root pkg
local pkg_fn = (import "PKG_ROOT");
local pkgInitial = pkg_fn(wake);

local root = wake._private.recurseDefinePkg(wake, pkgInitial);

{
    root: wake._private.simplify(root),
    all: wake._private.recurseSimplify(root),
}
