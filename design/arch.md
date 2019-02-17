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
- If `from=./path` then it gets resolved by the `pkg_resolver` directly.
- If `from=wake.exec(ePkg, ...)` then all calls getPkg using `ePkg` are put in a list
  and serialized to that call. `ePkg` then returns a coresponding list of the pkg-ids.
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
   a symlink in `.wake/pkgs` if it does and return the path. For pkgs to a
   local path, it must put the pkg in universal storage and return the symlink.
   (DONE)
1. If the pkg does not exist, the `getPkg` is passed to the pkg in `exec`. If
   that pkg doesn't exist, it waits until it does. The exec pkg must download
   the pkg to `.wake/downloaded/pkgs/<pkg-id>` and return that path.
1. The `wake_pkg_resolver` will again be called with the downloaded path. It
   should move the files to their proper place and create a synmlink in
   `.wake/pkgs`


## [[.module_resolution]] `module_resolution` phase

The module resolution phase happens after all `pkg` are resolved.

It starts by calling the module at pkg root, called `root`.

```
local pkg = root;
local module = root.modules.{mod};


```


