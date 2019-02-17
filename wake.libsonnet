{
    local wake = self,

    TPKG_INFO: "pkg_info",
    TPKG: "pkg",
    TEXEC: "exec",
    TFILE: "file",
    _TPKG_DECLARE: "pkg_declare",
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
            type: self._TPKG_DECLARE,
            pkgInfo: pkgInfo,
            files: files,
            inputs: inputs,
            pkgs: pkgs,
            modules: modules,
        },

        local existing = wake._pkgResolve(config),
        return: if existing == null then
            pkgInfo // unresolved, will be resolved in a later passed
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
        type: self.TFILE,
        path: path,
        from: from,
        dump: dump,
    },

    // #SPC-helpers
    dir(): null,

    // TODO: this should do something
    _callNative(method, config): std.native(method)(std.manifestJsonEx(config, "  ")),

    _pkgResolve(config): wake._callNative("wake-pkg-resolver", config),
    _pkgRetrieve(config): wake._callNative("wake-pkg-retrieve", config),

    _instantiateModule(wake, moduleInfo, config): {
        local callConfigMaybe(config, selfModule) =
            if std.isFunction(config) then
                config(selfModule)
            else
                config,

        module: {
            pkg: moduleInfo.pkg,
            meta: moduleInfo.meta,
            config: config,

            local mods = moduleInfo.modules,

            // note that all of this is done lazily
            modules: {
                // mods are getModule objects

                [key]: {
                    local mInfo = mods[key].module,
                    local mConfig = mods[key].config,

                    return: wake.instantiateModule(
                        wake,
                        mods[key].module, 
                        callConfigMaybe(mConfig, self)
                    )
                }.return
                for key in mods
            },

            files: moduleInfo.files(wake, self),
            inputs: moduleInfo.inputs(wake, self),
            outputs: moduleInfo.outputs(wake, self),
            exec: moduleInfo.exec(wake, self),
        },
    },
}
