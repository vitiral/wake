#   Copyright 2019 Rett Berg (googberg@gmail.com)
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

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

    # An exact version of a pkgName, including the hash.
    , pkgVer(namespace, name, version, fingerprint):
        assert std.isString(hash) : "fingerprint must be a string";
        # Note: the version must be an exact semver, but is checked later.
        std.join(C.WAKE_SEP, [
            wake.pkgName(namespace, name),
            version,
            fingerprint,
        ])

    # Request to retrieve a pkg locally
    , pkgLocal(requestingPkgVer, path):
        [requestingPkgVer, path]

    # (#SPC-api.pkg): declare a pkg.
    #
    # Must be the only return of the function in PKG.libsonnet of the form
    #
    # ```
    # function(wake)
    #    wake.pkg(
    #        fingerprint=import "./.wake/fingerprint.json",
    #        name="mypkg",
    #        version="1.0.0",
    #        # ... etc
    #    )
    # ```
    , pkg(
        pkgVer,

        # General description of the pkg, for humans to read.
        # Type: string
        description=null,

        # Local paths (files or dirs) this pkg depends on for building.
        #
        # These are included when the full pkg is retrieved or setup in
        # a sandbox.
        #
        # Type: list[string]
        paths=null,

        # packages that this pkg depends on.
        #
        # Type: wake.deps object
        deps=null,

        # Exports of this pkg.
        #
        # > Called once the pkg has been fully defined (all dependencies resolved, etc).
        #
        # Type: function(wake, pkgDefined) -> Object
        exports=null,

        # TODO: move origin from module to here.
    ): {
        [C.F_TYPE]: C.T_PKG,
        [C.F_STATE]: C.S_DECLARED,
        fingerprint: fingerprint,
        namespace: U.stringDefault(namespace),
        name: name,
        version: version,
        description: description,
        pkgVer: wake.pkgVer(namespace, name, version, fingerprint.hash),
        paths: U.arrayDefault(paths),
        pathsDef: U.arrayDefault(pathsDef),
        pkgs: U.objDefault(pkgs),

        # lazy functions
        exports: exports,
    }

    # (#SPC-api.declareModule): declare how to build something.
    #
    # Modules are included in `pkg.exports`, as they are always tied to a pkg.
    # It is allowed for a pkg to export another pkg's modules (meta modules).
    #
    # Note that when `exec` is running it is within its `container` and has read
    # access to all files and inputs the local `pkg` the module is defined in, as
    # well as any pkgs and modules it is dependent on.
    , declareModule(
        # The pkg this module is defined in.
        pkg,

        # Module objects this module depends on.
        modules,

        # (lazy) Additional required `fsentry`s (files or dirs)
        #
        # Type: `function(wake, pkg, moduleDef) -> list[fsentry]`
        reqFsEntries=null,

        # function which behaves identically to `pkg.exports`.
        #
        # Contains a key/value map of the objects exported by this module.
        # Must not contain any unresolved objects (unresolved objects will
        # never be resolved).
        exports=null,

        # (lazy) The `exec` object used for building this module.
        #
        # Type `function(wake, module) -> wake.exec(...)`
        exec=null,

        # The origin of the module, such as author, license, etc
        origin=null,
    ): null # TODO

    # (#SPC-api.pathRef): Reference a path from within a pkg or module.
    #
    # This is used by `exec` to declare exactly which file to execute,
    # but it is also the standard way to "export" files for other packages and
    # modules to use.
    #
    # Returns: pathRefPkg or pathRefModule
    , pathRef(
        # A pkg or module to reference.
        ref,

        # The local path within the ref
        path,
    ): {
        assert U.isAtLeastDefined(ref) : "ref must be at least defined",

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

    # (#SPC-api.exec): specify an executable from within a pkg and container.
    #
    # All values given to `exec` must be immediately manifestable.
    #
    # ## How an `exec` operates.
    #
    # A temporary directory is instantiated by the **store** and set as the current
    # directory. This directory contains ONLY a `.wake/` directory
    # containing the following files:
    #
    # - `store`: an executable which follows @SPC-store, allowing the
    #   executable to retrieve links to paths of pkgVers.
    # - `exec.json`: the `exec` object directly manifested. Contains the
    #   configuration, etc.
    # - `wakeConstants.json`: the standard wakeConstants.json file, can be used to
    #   help construct APIs and read wake types.
    #
    # If the `container=wake.EXEC_LOCAL` then the `pathRef` is executed directly,
    # with the given env and args.
    #
    # Otherwise, the `container.pathRef` is executed with the additional env
    # var `__WAKE_CONTAINER=y`. It is then the job of the container exec to
    # set up the execution environment and run the exec.
    , exec(
        # is not necessarily the exec's
        # is determined by the container.
        pathRef,

        # or pkg should be executed, or
        # executed "anywhere."
        # must == `wake.LOCAL_CONTAINER`
        container,

        # List of strings to pass as arguments to the executable.
        #null,

        # be an object of strings
        # for the keys and values.
        #
        # Consider using `config` instead.
        #
        # Anything beginning with `__WAKE` is reserved for use by wake.
        env=null,
    ): {
        [C.F_TYPE]: C.T_EXEC,
        [C.F_STATE]: C.S_DEFINED,

        assert U.isPathRef(pathRef) : "pathRef is wrong type",
        assert container == C.EXEC_LOCAL || U.isExecLocal(container) :
            "container must == EXEC_LOCAL or a container which is EXEC_LOCAL",

        pathRef: pathRef,
        container: container,
        config: config,
        args: U.arrayDefault(args),
        env: U.objDefault(env),
    }

    , _private: {
        local P = self

        , F_IDS: {
            'pkgVer': null,
            'pkgReq': null,
        }

        , unresolvedPkg(pkgReq, from, usingPkg):  {
            [C.F_TYPE]: C.T_PKG,
            [C.F_STATE]: C.S_UNRESOLVED,
            exec: null,

            pkgReq: pkgReq,
            usingPkg: usingPkg,
            from: if usingPkg == null then
                assert std.isString(from) : "from must be a local path if usingPkg=null";
                from
            else
                assert std.isString(usingPkg) : "usingPkg must be a string representing the pkg key";
                if std.isString(from) then
                    [from]
                else
                    assert std.isArray(from) :
                        "from must be either a string or array[string] if usingPkg is specified";
                    from
        }

        # Used to lazily define the exports of the pkg and sub-pkgs.
        , recurseDefinePkg(wake, pkg): {
            local this = self,
            local _ = std.trace("recurseDefinePkg in " + pkg.pkgVer, null),
            local recurseMaybe = function(depPkg)
                if U.isUnresolved(depPkg) then
                    depPkg
                else
                    P.recurseDefinePkg(wake, depPkg),

            returnPkg: pkg + {
                # Do a first pass on the pkgs.
                local pkgsPass = {
                    [dep]: recurseMaybe(pkg.pkgs[dep])
                    for dep in std.objectFields(pkg.pkgs)
                }

                , [C.F_STATE]: if P.hasBeenDefined(pkg, this.returnPkg) then
                    C.S_DEFINED else pkg[C.F_STATE]

                , local defineGetPkg = function(depPkg)
                    if U.isUnresolved(depPkg) then
                        if depPkg.usingPkg == null then
                            depPkg
                        else
                            _P.handleGetPkgFromExec(this.returnPkg, depPkg)
                    else
                        depPkg

                , pkgs: {
                    [dep]: defineGetPkg(pkgsPass[dep])
                    for dep in std.objectFields(pkgsPass)
                }

                , exports:
                    if U.isDefined(this.returnPkg) then
                        local out = pkg.exports(wake, this.returnPkg);
                        assert std.isObject(out)
                            : "%s exports did not return an object"
                            % [this.returnPkg.pkgVer];
                        out
                    else
                        null
            }
        }.returnPkg

        , handleGetPkgFromExec(parentPkg, getPkg):
            local pkgName = getPkg.usingPkg;
            assert pkgName in parentPkg.pkgs :
                parentPkg.pkgVer + " does not contain " + pkgName;
            local execPkg = parentPkg.pkgs[pkgName];

            if U.isAtLeastDefined(execPkg) then
                getPkg + {
                    exec: U.getKeys(execPkg.exports, getPkg.from),
                }
            else
                getPkg

        # Return if the newPkg is defined.
        , hasBeenDefined(oldPkg, newPkg):
            local definedCount = std.foldl(
                function(prev, v) prev + v,
                [
                    U.boolToInt(U.isDefined(newPkg.pkgs[dep]))
                    for dep in std.objectFields(newPkg.pkgs)
                ],
                0,
            );
            definedCount == std.length(oldPkg.pkgs)

        , recurseSimplify(pkg):
            if U.isUnresolved(pkg) then
                [pkg]
            else
                local simpleDeps = [
                    P.recurseSimplify(pkg.pkgs[dep])
                    for dep in std.objectFields(pkg.pkgs)
                ];
                [P.simplify(pkg)] + std.flattenArrays(simpleDeps)

        , simplify(pkg): {
            [C.F_TYPE]: pkg[C.F_TYPE],
            [C.F_STATE]: pkg[C.F_STATE],
            pkgVer: pkg.pkgVer,
            description: pkg.description,

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
