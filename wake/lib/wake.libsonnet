{
    local wake = self,
    local U = wake.util,

    # Fields
    F_TYPE: "__WAKETYPE__",
    F_STATE: "__WAKESTATE",

    # Types
    T_OBJECT: "object",
    T_PKG: "pkg",
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

    // A pkg requirement with a semantic version.
    //
    // This is used as (partof) the filepath for pkgs and modules.
    pkgReq(name, versionReq=null, namespace=null):
    {
        local versionStr = U.stringDefault(versionReq),
        local namespaceStr = U.stringDefault(namespace),
        local hasComma = function(s) U.containsChr(',', s),

        assert std.length(name) > 3: "name length must be > 3",
        assert !hasComma(name): "name must not contain ','",
        assert !hasComma(versionStr): "versionReq must not contain ','",
        assert !hasComma(namespaceStr): "namespace must not contain ','",

        result: '%s,%s,%s' %[
            name,
            versionStr,
            namespaceStr,
        ],
    }.result,

    pkgId(name, version, namespace, hash): {
        assert std.isString(hash) : "hash must be string",
        // Note: the version must be an exact semver, but is checked later.
        return: "%s|%s" % [
            wake.pkgReq(name, version, namespace),
            hash,
        ],
    }.return,

    getPkg(pkgReq): {
        # TODO: check in completePkgs first
        local pkgDefs = wake._private.pkgDefs,
        local pkgCompletes = wake._private.pkgCompletes,

        return: if pkgReq in pkgDefs then
            local pkgFn = pkgDefs[pkgReq];
            pkgFn(wake)
        else
            wake._private.unresolvedPkg(pkgReq)
    }.return,

    // Declare a pkg.
    //
    // Must be the only return of the function PKG.libsonnet.
    declarePkg(
        hash,
        // The name of the pkg.
        //
        // Type: string
        name,

        // The exact version of the pkg.
        //
        // Type: string
        version,

        // the (optional) namespace of the pkg.
        //
        // Type: string
        namespace=null,


        // pkgs that this pkg depends on. 
        //
        // Type: object of key/getPkg(...) pairs
        pkgs=null,

        // Exports of this pkg. 
        //
        // Called once the pkg has been fully defined (all dependencies resolved, etc).
        //
        // Type: function(wake, pkgDefined) -> Object
        exports=null,
    ): {
        [wake.F_TYPE]: wake.T_PKG,
        [wake.F_STATE]: wake.S_DECLARED,
        hash: hash,
        name: name,
        version: version,
        namespace: namespace,
        pkgId: wake.pkgId(name, version, namespace, hash),
        pkgs: U.objDefault(pkgs),
        exports: exports,
    },

    _private: {
        local P = self,

        unresolvedPkg(pkgReq):  {
            [wake.F_TYPE]: wake.T_PKG,
            [wake.F_STATE]: wake.S_UNRESOLVED,
            pkgReq: pkgReq,
        },

        recurseDefinePkg(wake, pkg): {
            local this = self,

            returnPkg: pkg + {
                [wake.F_STATE]: if P.isDefined(pkg, this.returnPkg) then
                    wake.S_DEFINED else pkg[wake.F_STATE],

                exports: {
                    return: pkg.exports(wake, this.returnPkg),
                    assert std.isObject(self.return) 
                        : "%s exports did not return an object"
                        % [this.returnPkg.pkgId],
                }.return,

                pkgs: {
                    [dep]: P.recurseDefinePkg(wake, pkg.pkgs[dep])
                    for dep in std.objectFields(pkg.pkgs)
                },
            }
        }.returnPkg,

        isDefined(oldPkg, newPkg): {
            local definedCount = std.foldl(
                function(prev, v) prev + v,
                [
                    U.toInt(U.isDefined(newPkg.pkgs[dep]))
                    for dep in std.objectFields(newPkg.pkgs)
                ],
                0,
            ),
            return: definedCount == std.length(oldPkg.pkgs),
        }.return,
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
        containsChr(c, str): !(std.length(std.splitLimit(str, c, 1)) == 1),
        isVersionSingle(ver): {
            local arr = ver.split(ver, '.')
        },
    },
}
