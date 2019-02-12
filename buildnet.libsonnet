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
    TYPE_MODULE_URL: "module_url",
    TYPE_EXEC: "exec",
    TYPE_REF: "ref",

    // Define a module to be built.
    //
    // A module is ONLY a hash of its name, version, inputs, and declared
    // outputs (the paths themselves).
    //
    // - 'name': the name to give to the module. This is only used as a hash
    //   and for publishing and user-reference.
    // - `inputs`: list of files, dirs, module_[path/url/etc] or refs.
    // - `outputs`: Flat Object of files, modules or refs (no dirs).
    // - `exec`: path or ref to a single `.wasm` target to execute. It
    //   will be executed in a sandbox with the inputs unpackaged in
    //   its local directory and the module manifest piped in as json through
    //   stdin.
    // - 'version': currently a non-enforced version string that can be empty.
    //   Used in the hash.
    module(name, inputs, outputs, exec=null, version=null):: {
        type: bnet.TYPE_MODULE,
        name: name,
        inputs: inputs,
        outputs: outputs,

        assert exec != '__exec__.wasm',
        exec: exec,
        version: version,
    },


    // Use an output provided by another module as an object.
    ref(mod, path):: {
        type: bnet.TYPE_REF,
        path: path,
    },

    // A path or ref to a single `.wasm` target to execute. It
    // will be executed in a sandbox as part of a `module` with the inputs
    // unpackaged in its local directory and the module manifest piped in as
    // json through stdin.
    //
    // You can pass optional args which are included in the command. It is recommended
    // to keep them extremely short.
    exec(path, args = null):: {
        type: bnet.TYPE_EXEC,
        path: path,
        args: args,
    },

    hash(enc, value):: {
        type: bnet.TYPE_HASH,
        enc: enc,
        value: value,
    },

    file(path):: {
        assert assert_path(path),
        path: path,
        type: bnet.TYPE_FILE,
    },

    dir(path):: {
        assert assert_path(path),
        path: path,
        type: bnet.TYPE_DIR,
    },

    // path to another module
    module_path(path):: {
        assert assert_path(path),
        path: path,
        type: bnet.TYPE_MODULE_PATH,
    },

    // url to another module to be downloaded
    module_url(url, hash):: {
        assert hash.type == bnet.TYPE_HASH,
        assert std.asciiUpper(hash.enc) in bnet.HASH_ENC_VALID,
        url: url,
        hash: hash,
        type: bnet.TYPE_MODULE_URL,
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
