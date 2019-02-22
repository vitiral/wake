{
    local wake = self,

    # Fields
    F_TYPE: "__WAKETYPE__",
    F_STATE: "__WAKESTATE",

    # Types
    T_OBJECT: "object",
    T_PKG: "pkg",
    T_GLOBAL: "global",
    T_MODULE: "module",
    T_FILE: "file",

    # States
    S_UNRESOLVED: "unresolved",
    S_DECLARED: "declared",
    S_DEFINED: "defined",
    S_COMPLETED: "completed",

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

    declarePkg(pkgInfo, pkgs=null, exports=null): {
        [wake.F_TYPE]: wake.T_PKG,
        [wake.F_STATE]: wake.S_DECLARED,
        pkgInfo: pkgInfo,
        pkgs: wake.util.objDefault(pkgs),
        exports: exports,
    },

    _private: {
        unresolvedPkg(pkgInfo):  {
            [wake.F_TYPE]: wake.T_PKG,
            [wake.F_STATE]: wake.S_UNRESOLVED,
            pkgInfo: pkgInfo,
        },

        recurseExports(wake, pkg): {
            result: pkg + {
                exports: {
                    "added": 42,
                },
            }
            // result: pkg + {
            //     exports: {
            //         [key]: pkg.exports[key](wake, pkg)
            //         for key in std.objectFields(pkg.exports)
            //     },
            //     pkgs: {
            //         [key]: wake._private.recurseExports(wake, pkg.pkgs[key]),
            //         for key in std.objectFields(pkg.pkgs)
            //     },
            // }
        }.result,
    },

    util: {
        local U = self,

       isWakeObject(obj):
           std.isObject(obj)
           && (wake.TTYPE in obj),

       isPkg(obj):
            U.isWakeObject(obj) && obj[wake.F_TYPE] == wake.T_PKG,

        // Return whether the object is defined or still needs to be resolved.
        //
        // Can be used in exported variables, etc to wait for the next cycle.
        isDefined(obj):
            assert wake.util.isWakeObject(obj) : "value must be a wake object";

            obj[wake.F_STATE] == wake.S_DEFINED
            || obj[wake.F_STATE] == wake.S_COMPLETED,

        UNRESOLVED: {
            [wake.F_TYPE]: wake.T_OBJECT,
            [wake.F_STATE]: wake.S_UNRESOLVED,
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
