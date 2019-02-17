{
    local wake = self,

    TPKG_INFO: "pkg_info",
    TPKG: "pkg",
    TEXEC: "exec",
    TFILE: "file",
    _TFILE_DEC: "file_declare",
    _TPKG_DEC: "pkg_declare",
    _TPKG_GET: "pkg_get",

    pkgInfo(name, version, namespace): {
        type: self.TPKG_INFO,
        name: name,
        version: version,
        namespace: namespace,
    },

    pkg(name, version, namespace=null, files=null, inputs=null, pkgs=null, modules=null): {
        local pkgInfo = pkgInfo(name, version, namespace),
        local config = {
            type: self._TPKG_DEC,
            pkgInfo: pkgInfo,
            files: files,
            inputs: inputs,
            pkgs: pkgs,
            modules: modules,
        },

        local existing = wake._pkgResolve(config),
        return: if existing == null then
            pkgInfo // unresolved, will be resolved in a later pass
         else
            wake.pkgs[existing]
    }.return,

    getPkg(pkgInfo, from, global=null, permissions=null): {
        local config = {
            type: self._TPKG_GET,
            pkgInfo: pkgInfo,
            from: from,
            global: global,
            permissions: permissions,
        },
        local existing = wake._pkgResolve(config),

        return: if existing == null then
            local _ = wake._pkgRetrieve(config);
            pkgInfo // unresolved, will be retrieved in a later pass
        else
            wake.pkgs[existing],
    }.return,

    module(pkg, modules, files, outputs, exec, meta): {
        local moduleInfo = {
            pkg: pkg,
            modules: modules,
            meta: meta,

            // lazy inputs
            files: files,
            outputs: outputs,
            exec: exec,
        },

        return: moduleInfo,
    }.return,

    getModule(moduleInfo, config): {
        local configuredModule = {
            "module": moduleInfo,
            "config": config,
        },

        return: configuredModule,
    }.return,

    exec(path, config=null, args=null, env=null): {
        type: self.TEXEC,
        config: config,
        args: args,
        env: env,
    },

    file(path, from=null, dump=false): {
        type: self.TFILE_DEC,
        path: path,
        from: from,
        dump: dump,
    },

    // #SPC-helpers
    dir(): null,

    _callNative(method, config): std.native(method)(std.manifestJsonEx(config, "  ")),

    // TODO: implement importing mechanics to find the pkg cache.
    // The resolver must always make it linked at
    // `.__wake__/pkgs.libsonnet` in every directory when config=_TPKG_PKGS
    _pkgs: import "wake::pkgs",

    // TODO: implement the resolver. It must handle _TPKG_DEC and _TPKG_GET
    _pkgResolve(config): wake._callNative("wake-pkg-resolver", config),

    // TODO: implement the resolver. It must handle _TPKG_GET
    _pkgRetrieve(config): wake._callNative("wake-pkg-retrieve", config),

    _instantiateModule(wake, moduleDec, config): {
        local callConfigMaybe(config, selfModule) =
            if std.isFunction(config) then
                config(selfModule)
            else
                config,

        return: {
            local getMods = moduleDec.modules,

            pkg: moduleDec.pkg,
            meta: moduleDec.meta,
            config: config,
            modules: {
                [key]: {
                    local mInfo = getMods[key].module,
                    local mConfig = getMods[key].config,

                    return: wake.instantiateModule(
                        wake,
                        getMods[key].module,
                        callConfigMaybe(mConfig, self)
                    )
                }.return
                for key in getMods
            },

            files: moduleDec.files(wake, self),
            inputs: moduleDec.inputs(wake, self),
            outputs: moduleDec.outputs(wake, self),
            exec: moduleDec.exec(wake, self),
        },
    }.return,
}
