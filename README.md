# ⏾🌊🛠 **wake** software's true potential

> **!! EXTREMELY EXPERIMENTAL, IN DESIGN !!**
>
> Status: this project has demonstrated (to the author) that the functionality
> it aims to accomplish is within reach, but is not yet functional. Currently
> it can only store local dependencies in a store and resolve a local PKG file.

**wake** is a functional package manger and build system for the web. Its basic
architecture is to enable the utmost _simplicity_ and _extensibility_ in a pkg
and build system. It is inspired from other build tools such as Nix, Bazel and
portage but is not related to any of them directly.

Its tennets are:
- **Simplicity**: pkg retrieval and module builds are fully reproducible and are
  simply inputs and outputs which can be hashed. The build language is
  [jsonnet], which is familiar, full featured and easy to understand.
- **Orthogonal features**: wake has very few features on its own, letting its
  simple extensibility provide features for any specific usecase (large or
  small). Jsonnet is kept pure (no native extenstions), while analyzing the
  build tree is done in easy to understand (and debug) cycles.
- **Build once, build anywhere**: specificying containers or pkg retrievers is
  done inline with the rest of the build system, allowing developers and
  organizations to fully control how their build system should scale. Once a
  module is built, it can always be used from the cache without any worry of
  its determinism.

The basic questions that wake is trying to answer is "why is it so hard
to include software as a dependency" and "why do I have to rebuild something
that has already been built with the exact same environment by an agent I
trust"? Both of these questions are ones which wake can and will answer.

For more information on how wake is being designed, check out the
[ARCHITECTURE](ARCHITECTURE.md) docs.

[jsonnet]: https://jsonnet.org/


## Future goals
Wake is currently in the early implementation phase. The following features are planned
before version 0.1.0 (alpha):

- (60% complete) `wake.libsonnet` library
- (90% complete) local pkg resolution overrides
- (0% complete) `pkg-retrieval` plugin
- (0% complete) `fsentry-resolver` plugin
- (0% complete) pkg tree resolution
- (0% complete) exec implementation
- (0% complete) exec.container implementation

It is believed by the author that once the above work is complete, wake will be
usable as an alpha quality product.

The goals afterwards are:
- Add a pkg-retriever to retrieve and auto-generate [portage] and ebuild
  packages, allowing for fast expansion of supported features.
- Nix-pkg integration (possible)
- Support of other language rules, especially the google ones.

[portage]: https://wiki.gentoo.org/wiki/Portage


# Notice
I am an employee at google but this software is made soley by me in my freetime
and is not endorsed or sponsored by google in any way.


# LICENSE

See the [LICENSE](LICENSE.md) file.

```
#   Copyright 2019 Rett Berg (googberg@gmail.com)
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
```
