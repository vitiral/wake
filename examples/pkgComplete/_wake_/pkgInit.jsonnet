// instantiate the wake library and user overrides.

local wakelib = import "../../../wake/lib/wake.libsonnet";
local user = (import "../../../wake/user.libsonnet")(wakelib);
local pkgDefs = (import "../_wake_/pkgDefs.libsonnet");

local wake =
    wakelib
    + {
        _private+: {
            pkgDefs: pkgDefs,
        },
    } + user;

// instantiate and return the root pkg
local pkg_fn = (import "../PKG.libsonnet");
local pkgInitial = pkg_fn(wake);

local pkg = wake._private.recurseExports(wake, pkgInitial);

{
    added: pkg.exports.added,
    exports: pkg.exports,
    root: pkg,
}
