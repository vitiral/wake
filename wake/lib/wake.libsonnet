{
    local wake = self,
    local U = wake.util,

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
        local versionStr = U.stringDefault(version),
        local namespaceStr = U.stringDefault(namespace),

        assert std.length(name) > 3: "name length must be > 3",
        assert !U.containsStr(',', name): "name must not contain ','",
        assert !U.containsStr(',', versionStr): "version must not contain ','",
        assert !U.containsStr(',', namespaceStr): "namespace must not contain ','",

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

    declarePkg(
        pkgInfo,
        pkgs=null,
        exports=null,
        useGlobals=null,
        setGlobals=null
    ): {
        [wake.F_TYPE]: wake.T_PKG,
        [wake.F_STATE]: wake.S_DECLARED,
        pkgInfo: pkgInfo,
        pkgs: U.objDefault(pkgs),
        exports: exports,
        useGlobals: useGlobals,
        setGlobals: setGlobals,
    },

    _private: {
        local P = self,

        unresolvedPkg(pkgInfo):  {
            [wake.F_TYPE]: wake.T_PKG,
            [wake.F_STATE]: wake.S_UNRESOLVED,
            pkgInfo: pkgInfo,
        },

        recurseDefinePkg(wake, pkg): {
            local this = self,

            result: pkg + {
                local definedCount = std.foldl(
                    function(prev, v) prev + v,
                    [
                        U.toInt(U.isDefined(this.result.pkgs[dep]))
                        for dep in std.objectFields(this.result.pkgs)
                    ],
                    0,
                ),
                local isDefined = definedCount == std.length(pkg.pkgs),
                [wake.F_STATE]: if isDefined then wake.S_DEFINED else pkg[wake.F_STATE],

                exports: pkg.exports(wake, this.result),

                pkgs: {
                    [dep]: P.recurseDefinePkg(wake, pkg.pkgs[dep])
                    for dep in std.objectFields(pkg.pkgs)
                },
            }
        }.result,
    },

    util: {
       isWakeObject(obj):
           std.isObject(obj)
           && (wake.F_TYPE in obj),

       isPkg(obj):
            U.isWakeObject(obj) && obj[wake.F_TYPE] == wake.T_PKG,

        // Return whether the object is defined or still needs to be resolved.
        //
        // Can be used in exported variables, etc to wait for the next cycle.
        isDefined(obj):
            assert U.isWakeObject(obj) : "value must be a wake object";

            obj[wake.F_STATE] == wake.S_DEFINED,

        UNRESOLVED: {
            [wake.F_TYPE]: wake.T_OBJECT,
            [wake.F_STATE]: wake.S_UNRESOLVED,
        },

        toInt(bool): if bool then 1 else 0,
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
