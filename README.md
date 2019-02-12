# Buildnet: the build system for the web

> **!! EXTREMELY EXPERIMENTAL, IN DESIGN !!**
>
> Status: This project currently has a valid libsonnet file... that is it.

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
  that have been compiled to a single `.wasm` binary (just lua currently). All wasm
  files are executed in a [wasmer](https://github.com/wasmerio/wasmer) sandbox.
- Json and Jsonnet: all configuration is jsonnet, which reduces to json when
  executing in wasm.


# LICENSE

See the [LICENSE](LICENSE.md) file.

   Copyright 2019 Rett Berg (googberg@gmail.com)

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
