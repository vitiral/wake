(import "wakeConstants.json") + {
    local wake = self,
    local U = wake.util,

    // A pkg requirement with a semantic version.
    //
    // This is used as (partof) the filepath for pkgs and modules.
    //
    // Errors:
    // - name and namespace must be length > 3
    // - It is an error for any field to have commas.
    // - versionReq must be a valid semverReq
    pkgReq(
        // The name of the pkgReq.
        name,

        // The version requirements of the pkgReq.
        //
        // wake will attempt to match the requirements, taking
        // into account other pkgs to use as few pkgs as possible.
        versionReq=null,

        // The namespace to find the pkg.
        namespace=null
    ): {
        local versionStr = U.stringDefault(versionReq),
        local namespaceStr = U.stringDefault(namespace),
        local namespaceLen = std.length(namespaceStr),
        local hasComma = function(s) U.containsChr(',', s),

        assert std.length(name) > 3: "name length must be > 3",
        assert namespaceLen == 0 || namespaceLen > 3: "namespace length must be > 3",
        assert !hasComma(name): "name must not contain ','",
        assert !hasComma(versionStr): "versionReq must not contain ','",
        assert !hasComma(namespaceStr): "namespace must not contain ','",

        result: '%s,%s,%s' %[
            name,
            versionStr,
            namespaceStr,
        ],
    }.result,

    // The exact pkgId of the pkg.
    //
    // This is similar to pkgReq except it is the _exact_ pkg, with the hash
    // included in the Id.
    pkgId(name, version, namespace, hash):
        assert std.isString(hash) : "hash must be string";
        // Note: the version must be an exact semver, but is checked later.
        "%s,%s" % [
            wake.pkgReq(name, version, namespace),
            hash,
        ],

    // Retrieve a pkg.
    //
    // #SPC-api.getPkg
    getPkg(
        // The pkgReq(...) to retrieve.
        pkgReq,

        // A string or exec(...) to use to retrieve the pkg from.
        from=null
    ):
        # TODO: check in completePkgs first
        local pkgsDefined = wake._private.pkgsDefined;
        local pkgCompletes = wake._private.pkgCompletes;

        if pkgReq in pkgsDefined then
            // TODO: must keep track of all ways we got the pkg
            local pkgFn = pkgsDefined[pkgReq];
            pkgFn(wake)
        else
            wake._private.unresolvedPkg(pkgReq, from),

    // Declare a pkg.
    //
    // Must be the only return of the function PKG.libsonnet.
    //
    // #SPC-api.declarePkg
    declarePkg(
        // The hash, **imported** from PKG.meta
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

        // Local paths (files or dirs) this pkg depends on for its definition.
        //
        // Paths used in the "define" phase must be included in this list.
        // Typically will just be items this PKG.libsonnet imports in some way.
        // This should be kept to a minimal size so that it can be retrieved
        // quickly.
        //
        // Note that .wake.libsonnet and PKG.libsonnet are automatically
        // included in this list.
        //
        // Type: list[string]
        defPaths=null,

        // Local paths (files or dirs) this pkg depends on for building.
        //
        // These are included when the full pkg is retrieved or setup in
        // a sandbox.
        //
        // Type: list[string]
        paths=null,

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

        defPaths: U.arrayDefault(defPaths),
        paths: U.arrayDefault(paths),
        pkgs: U.objDefault(pkgs),
        exports: exports,
    },

    _private: {
        local P = self,

        unresolvedPkg(pkgReq, from):  {
            [wake.F_TYPE]: wake.T_PKG,
            [wake.F_STATE]: wake.S_UNRESOLVED,
            pkgReq: pkgReq,
            from: from,
        },

        // Used to lazily define the exports of the pkg and sub-pkgs.
        recurseDefinePkg(wake, pkg): {
            local this = self,
            local _ = std.trace("recurseDefinePkg in " + pkg.pkgId, null),
            local recurseMaybe = function(depPkg)
                if U.isUnresolved(depPkg) then
                    depPkg
                else
                    P.recurseDefinePkg(wake, depPkg),

            returnPkg: pkg + {
                [wake.F_STATE]: if P.hasBeenDefined(pkg, this.returnPkg) then
                    wake.S_DEFINED else pkg[wake.F_STATE],

                exports:
                    local out = pkg.exports(wake, this.returnPkg);
                    assert std.isObject(out)
                        : "%s exports did not return an object"
                        % [this.returnPkg.pkgId];
                    out,

                pkgs: {
                    [dep]: recurseMaybe(pkg.pkgs[dep])
                    for dep in std.objectFields(pkg.pkgs)
                },
            }
        }.returnPkg,

        // Return if the newPkg is defined.
        hasBeenDefined(oldPkg, newPkg):
            local definedCount = std.foldl(
                function(prev, v) prev + v,
                [
                    U.boolToInt(U.isDefined(newPkg.pkgs[dep]))
                    for dep in std.objectFields(newPkg.pkgs)
                ],
                0,
            );
            definedCount == std.length(oldPkg.pkgs),

        recurseSimplify(pkg):
            if U.isUnresolved(pkg) then
                pkg
            else
                local simpleDeps = [
                    P.recurseSimplify(pkg.pkgs[dep])
                    for dep in std.objectFields(pkg.pkgs)
                ];
                [P.simplify(pkg)] + simpleDeps,

        simplify(pkg): {
            [wake.F_TYPE]: pkg[wake.F_TYPE],
            [wake.F_STATE]: pkg[wake.F_STATE],

            local onlyIdOrUnresolved = function(dep)
                if U.isUnresolved(dep) then
                    dep
                else
                    dep.pkgId,

            defPaths: pkg.defPaths,
            paths: pkg.paths,
            pkgId: pkg.pkgId,
            pkgs: {
                [dep]: onlyIdOrUnresolved(pkg.pkgs[dep])
                for dep in std.objectFields(pkg.pkgs)
            },
            exports: pkg.exports,
        },
    },

    util: {
        // Wake typecheck functions
        isWakeObject(obj):
            std.isObject(obj)
            && (wake.F_TYPE in obj),
        isPkg(obj):
             U.isWakeObject(obj) && obj[wake.F_TYPE] == wake.T_PKG,

        // Wake status-check functions.
        isUnresolved(obj):
            assert U.isWakeObject(obj) : "value must be a wake object";
            obj[wake.F_STATE] == wake.S_UNRESOLVED,

        isDefined(obj):
            assert U.isWakeObject(obj) : "value must be a wake object";
            obj[wake.F_STATE] == wake.S_DEFINED,

        // General Helpers
        boolToInt(bool): if bool then 1 else 0,
        containsChr(c, str): !(std.length(std.splitLimit(str, c, 1)) == 1),
        isVersionSingle(ver): {
            local arr = ver.split(ver, '.')
        },

        // Default functions return empty containers on null
        arrayDefault(arr): if arr == null then [] else arr,
        objDefault(obj): if obj == null then {} else obj,
        stringDefault(s): if s == null then "" else s,
    },
}
