Notes:
- "local packages" are just "locked packages" and they can only be defined by
  the root.
- package manager cmd has to be able to handle local paths (to PKG.libsonnet)
- these should be specified by `null`/empty as the namespace (maybe?)

# ⏾🌊🛠 **wake** software's true potential

> **!! EXTREMELY EXPERIMENTAL, IN DESIGN !!**
>
> Status: this project has demonstrated (to the author) that the functionality
> it aims to accomplish is within reach, but is not yet functional. Currently
> it can only store local dependencies in a store and resolve a local PKG file.

**wake** is a functional package manager and build system for the web. Its
basic architecture is to enable the utmost _simplicity_ and _extensibility_ in
a pkg and build system. It is inspired from other build tools such as Nix,
Bazel and portage but is not related to any of them directly.

Its tennets are:
- **Simplicity**: pkg retrieval and module builds are fully reproducible and are
  simply inputs and outputs which can be hashed. The build language is
  [jsonnet] which is familiar, full featured, deterministic, hermetic and easy
  to understand.
- **Orthogonal features**: wake has very few features on its own, letting its
  simple extensibility provide features for any specific usecase (large or
  small). Jsonnet is kept pure (no native extenstions), while analyzing the
  build tree is done in easy to understand (and debug) cycles.
- **Build once, build anywhere**: specificying containers or pkg retrievers is
  done inline with the rest of the build system, allowing developers and
  organizations to fully control how their build system should scale. Once a
  module is built, it can always be used from the cache without any worry of
  its determinism.

The basic use cases are:
- "normal" developers (open source, small companies, etc) should be able to
  depend on pkgs either localy (via a path) or from a server. Their language
  of choice should be easily export "plugins" that can retrieve pkgs from the
  standard pkg server and convert them to PKG.libsonnet. They should be able
  to run their builds either locally, on the "cloud", or a combination of the
  above as applicable. It should be easy for them to use their own
  configurations or get a built solution (examples: build flags, compiler
  versions, pkg retrievers used, file storage, etc)
- "large organizational" developers and devops should be able to override
  how pkgs are defined, retrieved, stored and built to fully control every
  aspect.
- Any developer should be able to use caches (public, private, enterprise)
  which store built modules. wake's determinism allows them to trust these
  completed builds as API compatibile with the dependency they would build
  locally.

All of the above features should be "native" to the user -- plugins are defined
as normal depdendencies of their `PKG.libsonnet` (but overrideable via a
`$WAKEPATH`). A pkg local directory is its own "environment" that has control
of exactly how it is built.

For more information on how wake is being designed, check out the
[ARCHITECTURE](ARCHITECTURE.md) docs.

[jsonnet]: https://jsonnet.org/


## Future goals
Wake is currently in the early implementation phase. The following features are planned
before version 0.1.0 (alpha):

- (70% complete) `wake.libsonnet` library
- (90% complete) local pkg resolution overrides
- (10% complete) pkg version tree resolution
- (0% complete) `pkg-retrieval` plugin
- (0% complete) `fsentry-resolver` plugin
- (0% complete) exec implementation
- (0% complete) exec.container implementation

It is believed by the author that once the above work is complete, wake will be
usable as an alpha quality product.

The goals afterwards are:
- (hopefully) Add a pkg-retriever to retrieve and auto-generate [portage] and ebuild
  packages, allowing for fast expansion of supported features.
- (probably) Nix-pkg integration
- (probably) Create external pkgs to Support common languages, especially the
  google ones.
- (pie in the sky) Support an end-to-end wasm build system, whereby all `exec`
  items are run in a wasm runtime, but which can build for any system. This
  would achieve the highest possible level of build simplicity (all inputs
  are wasm, all outputs could be wasm).

[portage]: https://wiki.gentoo.org/wiki/Portage


# Notice
I am an employee at google but this software is made soley by me in my freetime
and is not endorsed or sponsored by google in any way.


# License

The source code is Licensed under either of

* Apache License, Version 2.0, ([LICENSE-APACHE](LICENSE-APACHE) or
  http://www.apache.org/licenses/LICENSE-2.0)
* MIT license ([LICENSE-MIT](LICENSE-MIT) or
  http://opensource.org/licenses/MIT)

at your option.

Unless you explicitly state otherwise, any contribution intentionally submitted
for inclusion in the work by you, as defined in the Apache-2.0 license, shall
be dual licensed as above, without any additional terms or conditions.
