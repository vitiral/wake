# Buildnet: the build system for the web

> **!! EXTREMELY EXPERIMENTAL, IN DESIGN !!**
>
> Status: This project currently has a valid libsonnet file... that is it.

As a build tool, buildnet aims to be "the build tool of the web".

Its basic architecture is to enable the utmost _simplicity_ in the
build system. It is inspired from other build tools such as Nix and Bazel,
but is not related to any of them directly.

Its tennets are:

- Simplicity: module builds are fully reproducible and are simply inputs and
  outputs.  Furthermore, inputs and outputs can each be reduced to a _single
  file_ (which can be a `.nar` directory of files) and a _single json
  configuration_. Inputs can include other modules.
- Wasm: the only executable is `.wasm`. The only compilers supported are ones
  that have been compiled to a single `.wasm` binary (just lua currently). All
  wasm files are executed in a [wasmer](https://github.com/wasmerio/wasmer)
  sandbox.
- Json and Jsonnet: all configuration is jsonnet, which reduces to json when
  executing in wasm.

However, Buildnet is so much more than a build tool, as it includes the `effect`
object. `effect` corrupts any "build" so that it is no longer considered
reproducible (or hashable), but it allows for embedding arbitrary services
within the build+configuration system that is buildnet. Basically,
effects can depend on modules both for binaries and configuration but can do
things like:

- populate or migrate a database
- depend on other effects (i.e. depend on a database being populated)
- spawn services in the cloud, such as a webserver.


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
