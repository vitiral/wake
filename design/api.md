# SPC-api
partof: SPC-arch
###

This details the API of `wake.jsonnet`. See links in the ".subarts" below to
the implementation and further documentation.

The basic API of wake is:
- Declare a PKG.jsonnet which is must return a `function(wake)`, which itself returns
  a call to `wake.declarePkg(...)`
    - A pkg is _just data_ (files)
- The pkg then goes through multiple states as its dependencies are resolved.
  These states are _declared_ -> _defined_ -> [_ready_ ->] _completed_, where
  _ready_ is only for modules.
  - Closures on the pkg (like `exports`) are called when the pkg has achieved a
    state marked with the name of the input, i.e. `pkgDefined` is a pkg in
    state _defined_.
- Modules are of type `function(wake, pkgReady, config)` and return a call to
  `wake.defineModule`. Modules define what is built and how it is built.
  - Modules are hashed as the pkg (just data) the `config` passed to them, and
    finally the modules they depend on.

## Wake API

- [[.pkgId]]: the uniq id (including exact version and hash) of a specific
  pkg. Used for pkg lookup.
- [[.pkgReq]]: defines a semver requirement for a `getPkg` call to retreive.
- [[.getPkg]]: retrieve a pkg lazily.
- [[.declarePkg]]: declare a pkg.
- [[.declareModule]]: declare how to build something with a pkg.
- [[.fsentry]]: specify a file-system object within a pkg or module.
- [[.exec]]: a declared executable. Is typically a member of `module.exec`
  or can be a member of `exports` for a pkg or module.
