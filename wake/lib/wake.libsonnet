{
    local wake = self,

    TTYPE: "__WAKETYPE__",
    _UNRESOLVED_PREFIX: "unresolved",
    // general unresolved object, called by the user
    _TUNRESOLVED_OBJ: wake._UNRESOLVED_PREFIX + "Obj",
    _TUNRESOLVED_PKG: wake._UNRESOLVED_PREFIX + "Pkg",

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
        # TODO: check in completePkgs first
        local pkgDefs = wake._private.pkgDefs,
        local pkgCompletes = wake._private.pkgCompletes,

        return: if pkgInfo in pkgDefs then
            local pkgFn = pkgDefs[pkgInfo];
            pkgFn(wake)
        else
            wake._private.unresolvedPkg(pkgInfo)
    }.return,

    pkg(pkgInfo, pkgs=null, exports=null): {
        pkgInfo: pkgInfo,
        pkgs: wake.util.objDefault(pkgs),
        exports: exports,
    },

    _private: {
        unresolvedPkg(pkgInfo):  {
            [wake.TTYPE]: wake._TUNRESOLVED_PKG,
            pkgInfo: pkgInfo,
        },

        recurseExports(wake, pkg): {
            result: pkg + {
                exports: {
                    [key]: pkg.exports[key](wake, pkg)
                    for key in std.objectFields(pkg.exports)
                }
            }
        }.result,
    },

    util: {
        // Return whether the object is completed or still needs to be resolved.
        //
        // Can be used in exported variables, etc to wait for the next cycle
        // to complete a computation.
        isCompleted(obj):
            assert std.isObject(obj) : "value must be an object";
            assert wake.TTYPE in obj : "value must be a wake object";
            local t = obj[wake.TTYPE];
            if std.startsWith(t, wake._UNRESOLVED_PREFIX) then
                false
            else
                true,

        unresolved(): {
            [wake.TTYPE]: wake._TUNRESOLVED_OBJ,
        },

        arrayDefault(arr): if arr == null then [] else arr,
        objDefault(obj): if obj == null then {} else obj,
        stringDefault(s): if s == null then "" else s,
        containsStr(c, str):
        if std.length(std.splitLimit(str, c, 1)) == 1 then
            false
        else
            true,

    },
}
