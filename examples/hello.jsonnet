// hello.jsonnet

// This function will be called by the build system.
//
// - `bnet`: must exist and will be the buildnet jsonnet library.
// - `env`: must exist, and will be the current build environment.
//   contains things like language definitions, etc.

local m = function(bnet, env, say_name="Bob") {
    local inputs = {
        // local file
        hello_file: bnet.file("./hello.lua"),

        // defined `ref` in the environment
        lua: env.lang.lua,
    },

    local outputs = {
        hello: bnet.exec(
            inputs.lua,
            args=[inputs.hello_file, say_name],
        ),
    },

    return: bnet.module(
        name="hello",
        inputs=inputs,
        outputs=outputs,
    )
};


"hello"
