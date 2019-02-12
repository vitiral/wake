# REQ-arch

buildnet is architected upon the following pillars:

- `jsonnet` is the configuration language. All behavior from a user's
  perspective can be imported through the `buildnet.libsonnet` entry point.
  All configurations are representable in JSON.
- `wasm` is the sandboxing and execution model. All wasm is executed in a
  sandbox using `wasmer`.
- The core is written in `rust`, but could easily be written in any language.
- It is easy to extend the build system using any language that can compile
  to `wasm`. Languges which can cross-compile their _compiler_ to `wasm` can
  use buildnet as both a package manager and a build system.


# REQ-user
partof: REQ-arch
###

> Because jsonnet does not have API documentation rendering builtin, this
> artifact will be used as the user documentation.

To use jsonnet, a user first writes a `.jsonnet` file, which looks something
like `examples/hello.jsonnet  in this library.
