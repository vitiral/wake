# ⏾🌊🛠 wake software's true potential
#
# Copyright (C) 2019 Rett Berg <github.com/vitiral>
#
# The source code is Licensed under either of
#
# * Apache License, Version 2.0, ([LICENSE-APACHE](LICENSE-APACHE) or
#   http://www.apache.org/licenses/LICENSE-2.0)
# * MIT license ([LICENSE-MIT](LICENSE-MIT) or
#   http://opensource.org/licenses/MIT)
#
# at your option.
#
# Unless you explicitly state otherwise, any contribution intentionally submitted
# for inclusion in the work by you, as defined in the Apache-2.0 license, shall
# be dual licensed as above, without any additional terms or conditions.

local C = import "wakeConstants.json";

C + { local wake = self
    , local U = wake.util
    , local _P = wake._private

    # The package's namespace and name.
    , pkgName(namespace, name):
        local namespaceStr = U.stringDefault(namespace);
        local namespaceLen = std.length(namespaceStr);

        assert namespaceLen == 0 || namespaceLen > 3: "namespace length must be > 3";
        assert !_P.hasSep(namespaceStr): "namespace must not contain '#'";
        assert std.length(name) > 3: "name length must be > 3";
        assert !_P.hasSep(name): "name must not contain '#'";

        std.join(C.WAKE_SEP, [
            namespaceStr,
            name,
        ])

    # Specifies what versions of a package are required using a semver.
    , pkgReq(
        # The namespace to find the pkg.
        namespace,

        # The name of the pkg.
        name,

        # The semver requirements of the pkgName
        semver=null,

    ): {
        local semverStr = U.stringDefault(semver),

        assert !_P.hasSep(semverStr): "semver must not contain '@'",

        result: std.join(C.WAKE_SEP, [
            wake.pkgName(namespace, name),
            semverStr,
        ]),
    }.result

    # An exact version of a pkgName, including the digest.
    , pkgVer(namespace, name, version, digest):
        assert std.isString(digest) : "digest must be a string";
        # Note: the version must be an exact semver, but is checked later.
        std.join(C.WAKE_SEP, [
            wake.pkgName(namespace, name),
            version,
            digest,
        ])

    # Request to retrieve a pkg locally
    , pkgLocal(requestingPkgVer, path):
        [requestingPkgVer, path]

    # Declare a pkg.
    , pkg(
        pkgVer,

        # Description and other metadata regarding the origin of the package.
        pkgOrigin=null,

        # Local paths (files or dirs) this pkg depends on for building.
        paths=null,

        # packages that this pkg depends on.
        deps=null,

        # Function which returns the exports of this pkg.
        exports=null,
    ): {
        [C.F_TYPE]: C.T_PKG,
        [C.F_STATE]: C.S_DECLARED,
        pkgVer: pkgVer,
        pkgOrigin: pkgOrigin,
        paths: U.arrayDefault(paths),
        deps: U.objDefault(deps),

        # lazy functions
        exports: exports,
    }

    # Convert a pkg object into only it's digest elements.
    , pkgDigest(pkg): {
        [k]: pkg[k] for k in std.objectFields(pkg)
        if k != "exports"
    }

    # Declare dependencies for a package.
    , deps(
        unrestricted=null,
        restricted=null,
        restrictedMajor=null,
        restrictedMinor=null,
        global=null,
    ): {
        [C.F_TYPE]: C.T_DEPS,
        unrestricted: unrestricted,
        restricted: restricted,
        restrictedMajor: restrictedMajor,
        restrictedMinor: restrictedMinor,
        global: global,
    }

    # Declare how to build a module.
    , declareModule(
        pkg,
        modules,
        reqFsEntries=null,
        exports=null,
        exec=null,
        origin=null,
    ): null # TODO

    # Reference a path from within a pkg or module.
    , pathRef(
        # A pkg or module to reference.
        ref,

        # The local path within the ref
        path,
    ): {
        assert U.isAtLeastDefined(ref) : "ref must be defined",

        local vals = if U.isPkg(ref) then
            {type: C.T_PATH_REF_PKG, id: ref['pkgVer']}
        else
            assert false : "ref must be a pkg or a module.";
            null,

        [C.F_TYPE]: vals.type,
        [C.F_STATE]: C.S_DEFINED,
        [if U.isPkg(ref) then 'pkgVer' else "modVer"]: vals.id,
        path: path,
    }

    # Specify an executable from within a pkg and container.
    , exec(
        # is not necessarily the exec's
        # is determined by the container.
        pathRef,

        # or pkg should be executed, or
        # executed "anywhere."
        # must == `wake.LOCAL_CONTAINER`
        container,

        # List of strings to pass as arguments to the executable.
        params=null,
    ): {
        [C.F_TYPE]: C.T_EXEC,
        [C.F_STATE]: C.S_DEFINED,

        assert U.isPathRef(pathRef) : "pathRef is wrong type",
        assert container == C.EXEC_LOCAL || U.isExecLocal(container) :
            "container must == EXEC_LOCAL or a container which is EXEC_LOCAL",

        pathRef: pathRef,
        container: container,
        params: U.defaultObj(params),
    }

    # An error object. Will cause build to fail.
    , err(msg): {
        [C.F_TYPE]: C.T_ERROR,
        msg: msg,
    }


    , _private: {
        local P = self

        , recurseCallExports(wake, pkg): {
            local this = self,

            [C.F_TYPE]: pkg[C.F_TYPE],
            [C.F_STATE]: C.S_DEFINED,
            pkgVer: self.pkgVer,
            pkgDigest: wake.pkgDigest(this),

            local callExports = function(dep)
                if U.isUnresolved(dep) then
                    dep
                else
                    dep.pkgVer,

            local deps = {
                [dep]: getIdOrUnresolved(pkg.pkgs[dep])
                for dep in std.objectFields(pkg.pkgs)

            },

            returnPkg = pkg + {

            },
        }.returnPkg

        , simplify(pkg): {
            [C.F_TYPE]: pkg[C.F_TYPE],
            [C.F_STATE]: pkg[C.F_STATE],
            pkgVer: pkg.pkgVer,

            local getIdOrUnresolved = function(dep)
                if U.isUnresolved(dep) then
                    dep
                else
                    dep.pkgVer,

            pathsDef: pkg.pathsDef,
            paths: pkg.paths,
            # FIXME: pathsReq
            pkgs: {
                [dep]: getIdOrUnresolved(pkg.pkgs[dep])
                for dep in std.objectFields(pkg.pkgs)
            },
            exports: pkg.exports,
        }

        , recurseSimplify(pkg):
            if U.isUnresolved(pkg) then
                [pkg]
            else
                local simpleDeps = [
                    P.recurseSimplify(pkg.pkgs[dep])
                    for dep in std.objectFields(pkg.pkgs)
                ];
                [P.simplify(pkg)] + std.flattenArrays(simpleDeps)


        , hasSep(s): U.containsChr(C.WAKE_SEP, s)

        , getPkgName(str):
            local items = std.splitLimit(str, C.WAKE_SEP, 3);
            wake.pkgName(items[0], items[1])
    }

    , util: {
        # Wake typecheck functions
        isWakeObject(obj):
            std.isObject(obj)
            && (C.F_TYPE in obj)

        , isErr(obj):
             U.isWakeObject(obj) && obj[C.F_TYPE] == C.T_ERR

        , isPkg(obj):
             U.isWakeObject(obj) && obj[C.F_TYPE] == C.T_PKG

        # Wake status-check functions.
        , isUnresolved(obj):
            U.isWakeObject(obj)
            && obj[C.F_STATE] == C.S_UNRESOLVED

        , isDeclared(obj):
            U.isWakeObject(obj)
            && obj[C.F_STATE] == C.S_DECLARED

        , isDefined(obj):
            U.isWakeObject(obj)
            && obj[C.F_STATE] == C.S_DEFINED

        , isAtLeastDefined(obj):
            U.isDefined(obj)

        , isPathRef(obj):
             U.isWakeObject(obj) && (
                obj[C.F_TYPE] == C.T_PATH_REF_PKG
                || obj[C.F_TYPE] == C.T_PATH_REF_MODULE)

        , isExec(obj):
            U.isWakeObject(obj)
            && obj[C.F_TYPE] == C.T_EXEC

        , isExecLocal(obj):
            U.isExec(obj) && obj.container == C.EXEC_LOCAL

        # General Helpers
        , boolToInt(bool): if bool then 1 else 0
        , containsChr(c, str): !(std.length(std.splitLimit(str, c, 1)) == 1)

        # Retrieve a value from an object at an arbitrary depth.
        , getKeys(obj, keys, cur_index=0):
            local value = obj[keys[cur_index]];
            local new_index = cur_index + 1;
            if new_index == std.length(keys) then
                value
            else
                U.getKeys(value, keys, new_index)

        # Default functions return empty containers on null
        , arrayDefault(arr): if arr == null then [] else arr
        , objDefault(obj): if obj == null then {} else obj
        , stringDefault(s): if s == null then "" else s
    }
}
