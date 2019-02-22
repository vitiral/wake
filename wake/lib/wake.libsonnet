{
    local W = self,

    TTYPE: "__WAKETYPE__",
    _TPKG_UNRESOLVED: "pkgUnresolved",

    user(username, email=null): {
        username: username,
        email: email,
    },

    pkgInfo(name, version=null, namespace=null):
    {
        local versionStr = W.util.stringDefault(version),
        local namespaceStr = W.util.stringDefault(namespace),

        assert std.length(name) > 3: "name length must be > 3",
        assert !W.util.containsStr(',', name): "name must not contain ','",
        assert !W.util.containsStr(',', versionStr): "version must not contain ','",
        assert !W.util.containsStr(',', namespaceStr): "namespace must not contain ','",

        result: '%s,%s,%s' %[
            name,
            versionStr,
            namespaceStr,
        ],
    }.result,

    getPkg(wake, pkgInfo): {
        return: if pkgInfo in wake.pkgDefs then
            # TODO: check for pkgs first
            wake.pkgDefs[pkgInfo]
        else
            W._private.unresolvedPkg(pkgInfo)
    }.return,

    pkg(wake, pkgInfo, pkgs=null): {
        pkgInfo: pkgInfo,
        pkgs: W.util.arrayDefault(pkgs),
    },


    _private: {
        unresolvedPkg(pkgInfo):  {
            [W.TTYPE]: W._TPKG_UNRESOLVED,
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
