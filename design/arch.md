# REQ-purpose

Create an awesome build system.

# SPC-arch
partof: REQ-purpose
###

Wake is _both_ a pkg manager and a build system. The basic architecture of wake
is _simplicity_. Wake actually does very little, letting jsonnet and the
provided plugins do almost all of the heavy lifting.

> This architecture references [[SPC-api]] extensively.

## [[.cycle]]

One of the most important things to realize about wake is that it's architecture
is _lazy_. All phases run in an arbitrary number of cycles. All that is required is
that progress is made in each cycle. Therefore pkgs can depend on other pkgs
(or globals) which have not yet been found.

The purpose of cycles is simple: jsonnet is a language which _hates_ side effects, so
we never introduce them. Instead, we _fully resolve_ the json manifest (from
jsonnet's perspective) during each cycle, but keep track of items we still need
to retrieve/complete (native calls keep track of these unresolved items). We
then take all tasks that can be complete in this cycle, split them up by who
needs to do them, and run them in parallel -- letting the plugins handle how
_they_ do things in parallel.

There is only a single `std.native` call: `wake-store-action`, which passes an object
containing a type description and data of what needs to be resolved or checked.
This object is stored in an `HashSet` (to avoid deduplication) and processed
after the jsonnet manifest has been resolved.

There are several items that require actions:
- `_TGET_PKG`: a getPkg call was made in the retrieve-pkg phase. This is called
  every time because we need to see if multiple exec's are being used that they
  would return the same result.
- `_TSET_GLOBALS`: a hashmap of globals want to be set. Also contains the pkgId
  of who is setting them (can only be a single pkg in a tree).
- `_TNEED_GLOBALS`: a hashmap of globals that don't yet exist, and who needs
  them (pkgId). This is unused except to determine if the cycle has stalled.
- `_TBUILD_MODULE`: a module which needs to be built. Contains the full config
  for the module. This only happens in the `module-complete` phase.

## [[.pkg_complete]]
The pkg-complete phase is the first phase. A jsonnet file is created in
`$PWD/_wake_/pkgInit.jsonnet` containing:

```
// instantiate the wake library and user overrides.
local wakelib = import {WAKEPATH|/lib/wake.jsonnet;
local user = (import {WAKEPATH}/user.libsonnet)(wakelib);
local pkgsDef = (import "{PWD}/_wake_/pkgDefs.jsonnet")

local wake =
    wakelib    // the base library
    + pkgsDef  // (computed last cycle) defined pkgs
    + user;    // user settings

// instantiate and return the root pkg
local pkg_fn = (import {PWD}/PKG.libsonnet);
local pkg = pkg_fn(wake);

{
    wake: wake,
    root: pkg,
}
```

This file is executed repeatedly (multiple cycles). Each cycle, more calls
are made to `wake-store-action`, some of which are completed.

The following must happen:
- Calls to getPkg must be fulfilled by retrieving and defining the pkg (while
  also validating that different retrieval plugins don't cause chaos). These
  are just `pkgDef` which are stored in the local filesystem and linked
  relatively.
- Each successive cycle will have new calls to `getPkg`. Semver requirements
  will be re-interpreted in a _narrowing_ fashion each cycle, which can cause
  even more `getPkg` calls (and more cycles) (see _Appendix A_)

Eventually a single pkg tree will be chosen and the backend performs the following:
- One of the `exec`s will be re-executed to retrieve the full pkg
- The result will be passed to the `data-store` to put the pkg in the
  appropriate storage.

Congratulations, now all dependent pkgs are `state=pkg-completed`.

### Appendix A: Consideration of version changes as cycles progress
There is a possible issue in what happens during pkg resolution. Ideally a pkg
retriever would get as _few_ pkgs as possible that meet all semver
requirements. This ideal is difficult to implement, and is itself an NP-hard
problem. The problem is particularily difficult when the package requirements
and quanity can change every cycle (as they can here).

Let's say we had the following cycles:

- pkg-local requires pkg a(>=1.0), a(1.3 - 2.0), b(1.0 - 2.3)
- cycle A: we end up with a(2.0), b(3.0)
  - pkg-a(2.0) requires b(1.0 - 1.8)
- cycle B: we end up with a(2.0), b(1.8) (_b changed_)

One can imagine this cycle continuing for a very long time. The key to success
here are multiple points:
- Recall that pkgs are not built, and it is illegal to switch exec's for the same
  (name, namespace) pair. Therefore although pkgs, can ask for different pkgs, they
  cannot use _different exec_'s to do so.
- Cycles in the pkg graph are never allowed. Because of this, it should be not
  possible to create a cycle within loops (TODO: not proven).
- `pkg-retrieve` must simply return the pkg that _best matches that
  requirement_. It should not worry about other pkgs that have been retrieved.
- All "best packages" dependency trees must be resolved before full pkg download
  and module instantiation.

Also note that the metadata downloaded per-pkg is very small in this stage --
it should only include the files in `pkgFiles` except for the smallest of
packages. Therefore constructing the tree is relatively cheap, even over the
internet.

## [[.module_complete]] phase

The cmdline specifies which modules of `pkg` should be built. A jsonnet file
is created in `$PWD/_wake_/module|{key}|init.jsonnet` containing:

```
// instantiate the wake library and user overrides.
local wakelib = import {WAKEPATH|/lib/wake.jsonnet;
local user = (import {WAKEPATH}/user.libsonnet)(wakelib);
local wake = wakelib + user;

// instantiate and return the root pkg
local pkg_fn = (import {PWD}/PKG.libsonnet);
local pkg = pkg_fn(wake);

pkg.modules["{key}"](wake, pkg)
```

It starts by calling the module at pkg root, which we will call `root`.
There can be multiple roots, and they can be executed in parallel,
but we only need to consider them executed in series here.


