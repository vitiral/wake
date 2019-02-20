# REQ-purpose

Create an awesome build system.

# SPC-arch
partof: REQ-purpose
###

Wake is _both_ a pkg manager and a build system. The basic architecture of wake
is _simplicity_. Wake actually does very little, letting jsonnet and the
provided plugins do almost all of the heavy lifting.

> This architecture references [[SPC-api]] extensively.

There are two phases:
- pkg_resolution: retieves all pkg objects. During this phase `pkg` can be
  executed directly. This is the traditional "package management" phase.
- module_resolution: instantiates all modules using their `exec`. This is the
  traditional "build" or "make" phase.

One of the most important things to realize about wake is that it's architecture
is _lazy_. Pkgs can depend on other pkgs which don't yet exist, and it won't be
an error until the entire current tree has been resolved.

## [[.pkg_resolution]] `pkg_resolution` phase

The build system starts at `{working_dir}/PKG` and resolves it. This will results in
a single call to `pkg` which _fully resolves_ a json manifest. During this time, there
are several calls to `getPkg`. `getPkg` is implemented natively. Basically it:
- Checks if the pkg has already been gotten. If so, it returns the cached version.
- If `from=./path` then it is queued for the `pkg-initializer` to resolve directly.
- If `from=wake.exec(ePkg, ...)` then it is queued up according to execs and sent
  to the `pkg-exec`.
- If `from=wake.GLOBAL` it is put in a list of unresolved packages.
- Any pkgs that are not yet resolved are kept in that state. They can be resolved in
  a later loop.

The above continuously executes until all `getPkg` are resolved. If no pkgs remain
unresolved _and_ no pkgs were resolved in a cycle, then an error is raised.

> **Note**: although `override` can be used to override a global package, if
> that package has _ever_ been executed in this build cycle then it will raise an
> error (you can not override pkgs that have been executed).
>
> The exception to this rule is that the `wake_pkg_resolver` can be overriden.
> When null it uses a simple (builtin) file resolver. The `wake_pkg_downloader`
> may also be added in the future to download packages from a url.
>
> **Note:** if a pkg is retrieved by one exec, but the same pkg is requested
> using a different exec, then it will result in an error.
>
> For these reasons, it is generally recommended to use a single pkg retriever
> for any group of package types (i.e. namespace & language).
>
> **Note:** `pkg_retriever` _should_ typically retrieve the largest semver compliant
> pkg for any request.

Packages are retrieved and resolved thusly:
1. `myPkg.pkgs` includes a call to `getPkg(otherPkg)`
1. The `wake_pkg_resolver` is executed with the same args passed to `getPkg`.
   This must check if the `pkg` currently exists, error check it, and create
   a symlink in `_wake_/pkgs` if it does and return the path. For pkgs to a
   local path, it must put the pkg in universal storage and return the symlink.
1. If the pkg does not exist, the `getPkg` is passed to the pkg in `exec`. If
   that pkg doesn't exist, it waits until it does. The exec pkg must download
   the pkg to `_wake_/downloaded/pkgs/<pkg-id>` and return that path.
1. The `wake_pkg_resolver` will again be called with the downloaded path. It
   should move the files to their proper place and create a synmlink in
   `_wake_/pkgs`


### Consideration of version changes as cycles progress
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


### Consideration of execution container
Packages are instantiated as directory trees with:
- Their own files (pkgFiles and files)
- Their instantiated `config-instantiated.json`,
- includes the configuration files ([[SPC-rc]])

The first point is how should we use `getPkg.from<exec>`.  `exec.path` must:
- Be an executable.
- Only depend on files in `pkg.pkgFiles`
- Act _identically_ no matter what platform it is running on, as some are
  guaranteed to run on _at least_ the user's machine as well as the build
  nodes. It is okay for it to have builds for different platforms, but those
  builds must be deterministic and behave identically. It is therefore
  recommended to write it in a language like sh, wasm or python3.

If those conditions are met, then we can run it essentially anywhere.

Whew, okay. Now the issue I have been sidestepping -- what is with
the `exec.container` parameter? Before I dive in, let's discuss a few
things first:

- The platform we are building _for_ would be configured through the config,
  env or args parameter to `exec` (i.e.  `args =
  ["target=x86_64-unkown-linux-gnu"]`), and is not relevant for _which
  container is building the module_.
- Rather, we want a deterministic representation of the platform we are
  building _on_.
- However these are defined, they must obviously be a `GLOBAL` pkg of some
  kind.
- They are probably also themselves executables (i.e. docker). Many (excepting
  local builds) depend on some service already existing (i.e. a kubernettes
  cluster).
- We need to encapsulate several items:
  - Platform we are building on
  - How to execute the executable
  - How to use the information we have already collected such as instantaited
    pkgs and modules including downloaded files, linked files, etc
  - It seems that there has to be _some_ integration with the `pkg-initializer`,
    `module-resolver` and these `platform-resolver` objects.

## [[.module_resolution]] `module_resolution` phase

The module resolution phase happens after all `pkg` are resolved.

It starts by calling the module at pkg root, which we will call `root`.
There can be multiple roots, and they can be executed in parallel,
but we only need to consider them executed in series here.


