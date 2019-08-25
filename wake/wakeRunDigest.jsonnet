local wake = import "WAKELIB";
local pkg_fn = (import "PKG_ROOT");
{
    [k]: obj[k] for k in std.objectFields(obj) if k != "exports",
    pkg_fun(wake)
}
