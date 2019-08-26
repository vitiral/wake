# ⏾🌊🛠 **wake** software's true potential

> **!! EXTREMELY EXPERIMENTAL, IN DESIGN !!**
>
> Status: this project has demonstrated (to the author) that the functionality
> it aims to accomplish is within reach, but is not yet functional. Currently
> it can only store local dependencies in a store and resolve a local PKG file.

**wake** is a functional package manager and build system for the web. Its
basic architecture is to enable the utmost _simplicity_ and _extensibility_ in
a pkg and build system. It is inspired from other build tools such as [Nix],
[Bazel] and [portage] but uses [jsonnet] for configuration and is designed
explicitly for the next generation of portability with [wasi] and [wasm].

Its tennets are:
- **Simplicity**: pkg retrieval and module builds are fully reproducible and are
  simply inputs and outputs which can be hashed. The build language is
  [jsonnet] which is familiar, full featured, deterministic, hermetic and easy
  to understand.
- **Orthogonal features**: wake has very few features on its own and intends
  to only meet the goals of building the next generation of software built
  on [wasi].
- **Build once, build anywhere, run everwhere**: [wasi] is the only executable
  allowed in the build process. [wasi] is (\*will be) fast, cross-platform,
  language agnostic, and (mostly) deterministic. Wake packages will also
  largely produce [wasi] or [wasm] binaries, which means they can be run
  everywhere.

The basic use cases are:
- Easy to use package manager for developers with shared and composable
  dependencies. **Both** passing configurations to dependencies **and** using
  exported configurations provided by dependencies is easy.
- Building can happen locally **or** in the cloud, and can make use of community
  resources (i.e. open source cloud services, proprietary company services,
  IPFS, etc)
- The source and build artifacts of all packages can be secured by
  authorizations and cryptographic signatures.

For more information on how wake is being designed, check out the
[DESIGN](DESIGN.md) docs.

# Final Goal
The fundamental goal is to enable the next generation of software. Wake will make
it possible to seemelessy find and install software efficient (with shared
dependencies) and secure. Software and the libraries it depends on can be
shipped in small binary modules that can be run anywhere.

For developers, it means that writing and shipping cross-language software
can be done easily and quickly -- and the work of compiling software can be
shared. Your project has a large tree of commonly used depenendencies? How
would you like never waiting to compile most of them ever again?

Legacy build systems will still need to compile the OS itself to native code,
but could embed **wake** packages for most/all of their application binaries.
In addition, [wasi] will enable microkernels that run [wasi] in ring0 (see
[nebulet]).

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


[Nix]: https://nixos.org/nix/
[Bazel]: https://bazel.build
[portage]: https://wiki.gentoo.org/wiki/Portage
[jsonnet]: https://jsonnet.org/
[wasi]: https://wasi.dev
[wasm]: https://webassembly.org

[nebulet]: https://github.com/nebulet/nebulet

