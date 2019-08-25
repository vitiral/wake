local wake = import "WAKE_LIB";
local pkg_fn = (import "PKG_FILE");
local pkg = pkg_fn(wake);
{
    [k]: pkg[k] for k in std.objectFields(pkg)
    if k != "exports"
}
