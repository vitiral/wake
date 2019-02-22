{
    local wake = self,

    TTYPE: "__WAKETYPE__",
    _TPKG_UNRESOLVED: "pkgUnresolved",

    user(username, email=null): {
        username: username,
        email: email,
    },

    pkgInfo(name, version=null, namespace=null):
    {
        local versionStr = wake.util.stringDefault(version),
        local namespaceStr = wake.util.stringDefault(namespace),

        assert std.length(name) > 3: "name length must be > 3",
        assert !wake.util.containsStr(',', name): "name must not contain ','",
        assert !wake.util.containsStr(',', versionStr): "version must not contain ','",
        assert !wake.util.containsStr(',', namespaceStr): "namespace must not contain ','",

        result: '%s,%s,%s' %[
            name,
            versionStr,
            namespaceStr,
        ],
    }.result,

    getPkg(pkgInfo): {
        return: if pkgInfo in wake.pkgDefs then
            # TODO: check in completePkgs first
            wake.pkgDefs[pkgInfo]
        else
            wake._private.unresolvedPkg(pkgInfo)
    }.return,

    pkg(pkgInfo, pkgs=null): {
        pkgInfo: pkgInfo,
        pkgs: wake.util.arrayDefault(pkgs),
    },

    _private: {
        unresolvedPkg(pkgInfo):  {
            [wake.TTYPE]: wake._TPKG_UNRESOLVED,
            pkgInfo: pkgInfo,
        },
    },

    util: {
        arrayDefault(arr): if arr == null then [] else arr,
        stringDefault(s): if s == null then "" else s,
        containsStr(c, str):
        if std.length(std.splitLimit(str, c, 1)) == 1 then
            false
        else
            true,

    },
}
