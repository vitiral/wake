
{
    module(pkg, modules, files, outputs, exec, meta):: {
        local moduleInfo = {
            pkg: pkg,
            modules: modules,
            meta: meta,

            // lazy inputs
            files: files,
            inputs: inputs,
            outputs: outputs,
            exec: exec,
        },

        return: moduleInfo,
    }.return

    getModule(moduleInfo, config):: {
        local configuredModule = {
            "module": moduleInfo,
            "config": config,
        };

        return: configuredModule,
    }.return,

    instantiateModule(wake, moduleInfo, config):: {
        local callConfig(m, module) = {
            return: if type(m.config) == "function" then
                m.config(module)
            else
                m.config
            end
        }.return;

        module: {
            pkg: moduleInfo.pkg,
            meta: moduleInfo.meta,
            config: config,

            // note that all of this is done lazily
            modules: {
                key: instantiateModule(wake, c_m.module, callConfig(c_m, module))
                for (key, c_m) in moduleInfo.modules
            },

            files: moduleInfo.files(wake, self),
            inputs: moduleInfo.inputs(wake, self),
            outputs: moduleInfo.outputs(wake, self),
            exec: moduleInfo.exec(wake, self),
    }

    // example pkg "foo"

    pkgs: {
        "buildtools": wake.getPkg("buildtools", "core", "2.0+"),
    },

    modules(wake, pkg):: {
        local barPkg = pkg.pkgs.bar;

        bin: module(

            pkg=pkg,

            local config_bar_a(config): {
                {"setting": module.config.setting}
            },

            modules(wake, module):: {
                "bar_a": wake.getModule(barPkg.modules.bar_a, config_bar_a)
                "baz_a": wake.getModule(barPkg.pkgs.baz.modules.baz_a, {"force": false}),
            },

            // extra files to link/create from other modules or config
            files(wake, module):: {
                return: [
                    file("./dep/libbar.so", module.modules.bar_a.outputs.lib),
                ]
            },

            outputs(wake, module):: {
                bin: file("./bin/foo.wasm"),
            }

            exec(wake, module):: {
                local make = pkg.pkgs.buildtools.make.outputs;
                return: wake.exec(
                    make.bin, 
                    args=["build"], 
                    env=make.env + {"OPT": config.opt}
                ),
            },
        ),
    },

}
