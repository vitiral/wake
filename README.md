# wake: the pkg manager and build system for the web

> **!! EXTREMELY EXPERIMENTAL, IN DESIGN !!**
>
> Status: This project currently has a nearly valid libsonnet file and some
> experimental rust code... and that is it.

Wake is a functional package manger for the web. Its basic architecture is to
enable the utmost _simplicity_ in a pkg and build system. It is inspired from
other build tools such as Nix and Bazel, but is not related to any of them
directly.

Its tennets are:
- Simplicity: pkg retrieval and module builds are fully reproducible and are
  simply inputs and outputs which can be hashed.
- Orthogonal features: wake has very few features on its own, letting its
  simple extensibility provide features for any specific usecase (large or
  small).
- [jsonnet]: all configuration is jsonnet, which reduces to json when
  executing in wasm. [jsonnet] is a highly intuitive language made in the
  crucible of Google's configuration languages.

Wake diverges heavily from Nix and Blaze:
- Its goal (as a language) is to be _both_ a first-class pkg manager and a
  first class build system.
- Wake uses the [jsonnet] language for constructing its pkg and module (build)
  objects and provides very little functionality by itself.
- Wake is not built for any specific system, allowing globals to define usecase
  specific functionality.
- Wake has the concept of `sideEffects`, which are non-deterministic operations
  that can be executed on top of a build in order to (for example) run tests,
  start servers, analyze data, etc.

For more information on how wake is being designed, check out the
[ARCHITECTURE](ARCHITECTURE.md) docs.

[jsonnet]: https://jsonnet.org/

# LICENSE

See the [LICENSE](LICENSE.md) file.

```
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
```
