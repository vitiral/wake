// The buildnet library. The main entry point for users.
//
// See:
// #REQ-jsonnet
{
    local bnet = self,

    local assert_path(path) = {
        assert std.length(path) > 0 : "path cannot be empty",
        out: true,
    }.out,

    TYPE_HASH: "hash",
    HASH_ENC_VALID: {"AES-256": null},

    TYPE_FILE: "file",
    TYPE_DIR: "dir",
    TYPE_MODULE: "module",
    TYPE_MODULE_PATH: "module_path",
    TYPE_EXEC: "exec",
    TYPE_EFFECT: "effect",
    TYPE_REF: "ref",
    TYPE_REFS: "refs",
    EXEC_RESERVED: '__exec__.wasm',

    // Reference an output provided by another module as an object.
    //
    // > Note: Technically _all_ objects are resolved to a (module,path) pair,
    // > and are thus refered to as `ref`s.
    //
    // - `path`: the path to the reference within mod. If `path_new` is not given,
    //   the file will be put at the same relative path in the new module.
    // - `path_new`: specify where to put the path in the new module.
    ref(mod, path, path_new=null):: {
        type: bnet.TYPE_REF,
        mod: mod,
        path: path,
        path_new: path_new,
    },

    // Reference multiple outputs provided by another module.
    //
    // - `paths` is simply a list of paths to include directly in the local directory.
    // - `paths_move` is a list of `[path_old, path_new]` pairs, where the `path_old` will
    //   be taken from `mod` and put in the curent module's directory at `path_new`.
    refs(mod, paths=null, paths_move=null):: {
        assert paths != null 
            || std.length(paths) > 0 
            || paths_move != null
            || std.length(paths_move) > 0
            : "must provide either paths or paths_move",
        type: bnet.TYPE_REFS,
        mod: mod,
        paths: paths,
        paths_move: paths_move,
    },

    hash(enc, value):: {
        type: bnet.TYPE_HASH,
        enc: enc,
        value: value,
    },

    // Path to a single file.
    file(path):: {
        assert assert_path(path),
        path: path,
        type: bnet.TYPE_FILE,
    },

    // Helper function to create a path from a set of components.
    path(components):: join("/", components),

    // Path to a directory of files to glob-include.
    //
    // All matching sub files and directories will be recursively included,
    // except those listed in `exclude`.
    //
    // Conceptually returns: list[file]
    dir(include, exclude=null):: {
        type: bnet.TYPE_DIR,
        assert assert_path(path),
        include: include,
        exclude: exclude,
    },

    // Define a module to be built.
    //
    // A module is ONLY a hash of its name, version, inputs, and declared
    // outputs (the paths themselves).
    //
    // - 'name': the name to give to the module. This is only used as a hash
    //   and for publishing and user-reference.
    // - `inputs`: list of files, dirs, module_[path/url/etc] or refs.
    // - `outputs`: Flat Object of files, modules or refs.
    // - `exec`: path or ref to a single `.wasm` ref to execute. It
    //   will be executed in a sandbox with the inputs unpackaged in
    //   its local directory and the module manifest piped in as json through
    //   stdin.
    // - 'version': currently a non-enforced version string that can be empty.
    //   Used in the hash.
    module(name, inputs=null, outputs=null, exec=null, version=null):: {
        type: bnet.TYPE_MODULE,
        name: name,
        inputs: inputs,
        outputs: outputs,

        assert exec != bnet.EXEC_RESERVED,
        exec: exec,
        version: version,
    },

    // path to another module, with arguments to pass it.
    module_path(path, env, args=null):: {
        type: bnet.TYPE_MODULE_PATH,
        assert assert_path(path),
        path: path,
        args: args,
    },

    // A ref to a single `.wasm` file to execute, which must be part of the
    // module. It will be executed in a sandbox as part of a `module` with the
    // inputs unpackaged in its local directory.
    //
    //
    // - `config` is arbirary json, which will be passed through stdin.
    // - `args` are included in the command. It is recommended to keep them
    //   extremely short.
    exec(ref, config=null, args = null):: {
        type: bnet.TYPE_EXEC,
        ref: ref,
        args: args,
    },

    // Execute the exec from within the given module.
    //
    // `effect` can be used for:
    // - spinning up services in the cloud, such as a webserver
    // - instantiating test harnesses
    // - running tests
    // - collecting, storing and analyzing data
    // - implementing a custom package manager for buildnet
    //
    // Execution is done _outside_ of the normal build sandbox,
    // and additional permissions are given -- such as the ability
    // to create network sockets. This gives `effect` the ability
    // to create side-effects.
    //
    // `effect` has outputs and can be treated as a module by other `effect`
    // objects. If `is_pure` is `true` then it can even be treated as a module
    // by other modules, allowing (for example) creating custom module "package
    // managers".
    //
    // The outputs can also be useful for creating logs and scripts for
    // controlling and debugging the resulting `effect`.
    //
    effect(name, mod, exec, outputs=null, is_pure=false):: {
        assert std.isBoolean(is_pure),
        type: bnet.TYPE_EFFECT,
        name: name,
        mod: mod,
        exec: exec,
        is_pure: is_pure,
    },

    example_file: bnet.file("./example-file.txt"),
    example_dir: bnet.dir("./example-dir/"),
    example_url: bnet.module_url("foo.com", bnet.hash("AES-256", "f3e230a")),
    example_module: bnet.module(
        name='hello',
        inputs=[],
        outputs=[],
        exec=bnet.exec('hello.wasm')
    ),
}
