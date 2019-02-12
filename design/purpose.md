# REQ-arch

Buildnet is the web's build tool, which aims to utilize webassembly to
supercede the need for any other build tools.

Its basic architecture is to enable the utmost _simplicity_ in the
build system. It is inspired from other build tools such as Nix and Bazel,
but is not related to any of them directly.

Its tennets are:

- Simplicity: builds are simply inputs and outputs, which is reduced to a
  _single file_ (which can be a `.nar` directory of files) and a _single json
  configuration_. Inputs can include other builds.
- Wasm: the only executable is `.wasm`. The only compilers supported are ones
  that specify a `.wasm` binary.
- Json and Jsonnet: everything is jsonnet, which reduces to json.

## JSONNET Architecture

