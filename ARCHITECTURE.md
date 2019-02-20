# REQ-purpose
<details>
<summary><b>metadata</b></summary>
<b>partof:</b> <i>none</i></a><br>
<b>parts:</b><br>
<li><a style="font-weight: bold; color: #FF4136" title="SPC-API" href="#SPC-API">SPC-api</a></li>
<li><a style="font-weight: bold; color: #FF4136" title="SPC-ARCH" href="#SPC-ARCH">SPC-arch</a></li>
<b>file:</b> design/arch.md<br>
<b>impl:</b> <i>not implemented</i><br>
<b>spc:</b>0.00&nbsp;&nbsp;<b>tst:</b>0.00<br>
<hr>
</details>


Create an awesome build system.


# SPC-api
<details>
<summary><b>metadata</b></summary>
<b>partof:</b><br>
<li><a style="font-weight: bold; color: #FF4136" title="REQ-PURPOSE" href="#REQ-PURPOSE">REQ-purpose</a></li>
<b>parts:</b> <i>none</i></a><br>
<b>file:</b> design/api.md<br>
<b>impl:</b> <i>not implemented</i><br>
<b>spc:</b>0.00&nbsp;&nbsp;<b>tst:</b>0.00<br>
<hr>
</details>


Below are the different types/functions that make up the core API of wake.

Some special notes:

- files can only be defined in `files`. Any reference to a "file" in inputs or outputs
  (or anywhere) will simply be its raw data (json, string, etc).

## <span title="Not Implemented" style="color: #FF4136"><b><i>.pkgInfo</i></b></span> `pkgInfo(...)`
This is the information that defines a package identifier. It results in an
object which is used as part of other types.

Arguments:
- `name`: the name to give to the pkg. Must be at least 3 characters.
- `version`: semantic version used when resolving packages. Must be a valid
  semantic version requirement.
- `namespace=null`: a disambiguity between modules with the same name and
  version.  Used by organiations to control where modules come from. Must
  be at least 3 characters.

## <span title="Not Implemented" style="color: #FF4136"><b><i>.pkg</i></b></span> `pkg(...)`

Arguments:
- `pkgInfo`
- `pkgFiles=list[path]`: a list of paths to _local_ files which are necessary to
  define the `PKG` file. These files can then be downloaded when pkgs are being
  resolved, delaying the download of the entire source+data. Note that `PKG` is
  automatically included.
- `files=list[path]`: a list of paths to _local_ files to include. This automatically
  includes `PKG` itself and paths in `modules`, and is used to compute the hash of
  the PKG.  `inputs=function(wake, pkg) -> map`: function which takes in the
  instantiated `pkg` and returns a flat map of key/values. The values are
  _strongly typed_ and can include: ref, file.
- `pkgs`: flat map of key/pkgInfo. This is resolved first, and is used for
  finding and downloading pkgs.
- `modules=map[key, function]`: map of local modules of the pkg.
  `function(wake, pkg, config) -> moduleId`
- `globals=function(wake, pkg) -> map[key, value]`: set the global values which
  this instantiated pkg wants to set. See the _Globals_ section below.

> Note: the function defined in `inputs` is called at the beginning of this
> pkg's instantiation, only after all the `pkgs` this pkg is dependent on have
> been instantiated.

### Globals
Global values are a _single key_ which are utilized by other pkgs
and modules for configuration purposes. They are set by pkgs::gloabls
by pkgs which have `PERMISSION_DEFINE_GLOBAL`.

The `globals` function is called after the pkg is in state `pkg-done`.

Global values _must_ be one of (other types are not permitted):
- `pkg` objects, used as dependencies. Common examples include compilers,
  programming languages, and "standard" libraries.
- `config` objects, which are jsonnet objects that must not make calls to
  `getGlobal`.
- `exec` objects. This is necessary to override the default `pkg-retriever` and
  `pkg-resolver` objects, but is also commonly used for defining global
  containers. These objects _must_ have `container=wake.ANY`.

Globals can be set by any file in `$WAKEPATH/`, as well as by any pkg that has
`PERMISSION_DEFINE_GLOBAL`. It is an error to attempt to set a global to a
different value.

When globals are instantiated, their `wake` object is slightly altered such that
they cannot make calls to `getPkg` or `getModule`. They must therefore set a
global pkg via a reference from the `pkg` input.

Arguments:
- `key`: The global key to set, must be a non-empty string.
- `value`: the value to set. See above.


## <span title="Not Implemented" style="color: #FF4136"><b><i>.getGlobal</i></b></span> `getGlobal(...)`
Get a global value or return null if it does not yet exist.


## <span title="Not Implemented" style="color: #FF4136"><b><i>.getPkg</i></b></span> `getPkg(...)`
Retrieve a pkg.

Pkgs are _just data_ that can depend on other pkgs or the direct execution
of other pkgs (cannot depend on modules).

Arguments:
- `pkgInfo`
- `from`: one of:
  - ./path`: a reflike local directory where a `PKG.sonnet` file exists.
  - `wake.exec(ePkg, ...)`: to execute another pkg to retrieve the pkg.
    Typically this is gotten from a `getGlobal` call.
- `permisions=null`: permissions to grant the pkg. `defineGlobal` is required
  for the retrieved pkg to _itself_ define globals.

Returns: pkgInfo with an exact version.


## <span title="Not Implemented" style="color: #FF4136"><b><i>.module</i></b></span> `module(...)`

The definition of something to build.

Note that when `exec` is running it has read access to all files and inputs
the local `pkg` the module is defined in, as well as any pkgs and modules it
is dependt on.

Also note that when the inputs and outputs functions are called, the `pkg` will
be _fully resolved_, meaning that `module.pkgs.foo` will return the full `pkg`
object, and all paths will be resolved (the same is true for
`module.modules.foo`.

When instantiating (i.e. building) the module, `exec` will then be passed the
fully instantiated manifest, meaning it is just JSON (no jsonnet functions, etc).

Arguments:
- `pkg`: pkg this module came from.
- `modules`: dependencies of this module
- `files=function(wake, module) -> list[reflike]`: function which returns additional
  files (on top of `pkg.files`) to create/link for this specific module.
  Possibly new links, dumped configs, or references to inputs/outputs
  from `modules`. Cannot specify any references that don't already exist (i.e.
  new files), except `file(..., dump=true)`. The function is executed as the beginning
  of this module's instantiation (all the `modules` this module is dependent on
  have been instantiated.)
- `outputs=function(wake, module) -> map[str, value]`: function that returns a
  map contining the outputs of the module execution. Values are typically
  paths, lists of paths, or small jsonnet objects computed with only the
  `config`.
- `exec=function(wake, module) -> exec`: the execution to use to instantiate the module.
- `metadata`: the metadata of the module, such as author, license, etc. Not used
  in the hash of the module.


> Note: the functions defined in `files`, `inputs` and `outputs` are executed
> (lazily in parallel) as the beginning of a module's instantiation, after which
> the module's filesystem will be set up and `exec` called.

Returns: `moduleId`


## <span title="Not Implemented" style="color: #FF4136"><b><i>.getModule</i></b></span> `getModule(...)`
Retrieve a module from a pkg with a specified config.

Arguments:
- `module`
- `config`: either a raw config or a function which gets passed the module.

Returns: pkgInfo


## <span title="Not Implemented" style="color: #FF4136"><b><i>.exec</i></b></span> `exec(...)`
Specification for executing from within a pkg.

Arguments:
- `path`: local or linked path to execute
- `config`: config to pass to the executable as JSON via `stdin`
- `args`: list of strings to pass as arguments to the executable.
- `env`: environment variables to pass to the executable, resolved as strings.
  Consider using `config` instead.
  - all `file` objects will be converted to local paths `./path/to/file`
  - all raw strings will remain as strings
  - integers will be converted to a string
  - lists of strings will be converted to TODO(see nix)
  - !! values which serialize to be over 4kB will raise an error.
  - !! all other values will raise an error.
- `container`: an `exec` to use for where to execute. The specified
  `exec::container` must `=wake.ANY`.

The `exec` object will be serialized as `module.json` or `pkg.json`
(<a style="font-style: italic; color: #B10DC9" title="SPC-RC not found" >SPC-rc</a>) and included as part of `module-ready` (see <a style="font-style: italic; color: #B10DC9" title="SPC-RC not found" >SPC-rc</a>).  It is
the container's job to then properly execute it with all files and dependencies
made available.

## <span title="Not Implemented" style="color: #FF4136"><b><i>.file</i></b></span> `file(path, from=ref, dump=false)`
Refer to the file at `path`. If `from` is specified, will create a ln to a file
there using a file from another location (i.e. path, config blob, instantiated
pkg or module).

If dump is `true`, `from` should refer to a config blob. The manifest of the
config will be converted to json and dumped at `path`.

Returns: `file` object

```
struct File {
    path: PathBuf,
    from: Ref,
    dump: bool,
}
```


# SPC-arch
<details>
<summary><b>metadata</b></summary>
<b>partof:</b><br>
<li><a style="font-weight: bold; color: #FF4136" title="REQ-PURPOSE" href="#REQ-PURPOSE">REQ-purpose</a></li>
<b>parts:</b> <i>none</i></a><br>
<b>file:</b> design/arch.md<br>
<b>impl:</b> <i>not implemented</i><br>
<b>spc:</b>0.00&nbsp;&nbsp;<b>tst:</b>0.00<br>
<hr>
</details>


Wake is _both_ a pkg manager and a build system. The basic architecture of wake
is _simplicity_. Wake actually does very little, letting jsonnet and the
provided plugins do almost all of the heavy lifting.

> This architecture references <a style="font-weight: bold; color: #FF4136" title="SPC-API" href="#SPC-API">SPC-api</a> extensively.

There are two phases:
- pkg_resolution: retieves all pkg objects. During this phase `pkg` can be
  executed directly. This is the traditional "package management" phase.
- module_resolution: instantiates all modules using their `exec`. This is the
  traditional "build" or "make" phase.

One of the most important things to realize about wake is that it's architecture
is _lazy_. Pkgs can depend on other pkgs which don't yet exist, and it won't be
an error until the entire current tree has been resolved.

## <span title="Not Implemented" style="color: #FF4136"><b><i>.pkg_resolution</i></b></span> `pkg_resolution` phase

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
- includes the configuration files (<a style="font-style: italic; color: #B10DC9" title="SPC-RC not found" >SPC-rc</a>)

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
- However these are defined, they must obviously be a `GLOBAL` exec of some
  kind.
- We need to encapsulate several items:
  - Platform we are building on
  - How to execute the executable
  - How to use the information we have already collected such as instantaited
    pkgs and modules including downloaded files, linked files, etc
  - It seems that there has to be _some_ integration with the `pkg-initializer`,
    `module-resolver` and these `platform-resolver` objects.

## <span title="Not Implemented" style="color: #FF4136"><b><i>.module_resolution</i></b></span> `module_resolution` phase

The module resolution phase happens after all `pkg` are resolved.

It starts by calling the module at pkg root, which we will call `root`.
There can be multiple roots, and they can be executed in parallel,
but we only need to consider them executed in series here.


# SPC-helpers
<details>
<summary><b>metadata</b></summary>
<b>partof:</b> <i>none</i></a><br>
<b>parts:</b> <i>none</i></a><br>
<b>file:</b> design/api.md<br>
<b>impl:</b> <i>not implemented</i><br>
<b>spc:</b>0.00&nbsp;&nbsp;<b>tst:</b>0.00<br>
<hr>
</details>

These are helper functions are not part of the core types.

##  <span title="Not Implemented" style="color: #FF4136"><b><i>.dir</i></b></span>: `dir(include, exclude=null)`
Path to a directory of files to glob-include.

All matching sub files and directories will be recursively included,
except those listed in `exclude`.

Returns: `List[path]`


## SPC-rc
The following files are default or required:

### <span title="Not Implemented" style="color: #FF4136"><b><i>.user</i></b></span>
There are user configurations that are required, such as credentials and default
global pkgs. These files and folders are searched for at `$WAKEPATH/` and uses
a function in the wake library that is only available to users.

`user(...)`: user configuration

Define a user environment. This is necessary for running local commands and starting
the build process.

Arguments:
- username: the name to give to the user, used for logging.
- email: the user's email, used for logging.
- credential-resolver: a `sh` executable to use for generating credentials necessary
  to run external services. If it is defined, credentials will be requested for
  each pkg retrieved and resolved; as well as modules instantiated and sideEffect
  executed.
- pkg-retriever: set the _initial_ (overrideable) pkg retriever when building.
  The default one can only handle local paths.
- pkg-initializer: set the _initial_ (overrideable) pkg resolver. The default
  one can only store pkgs in `wakeGlobalDir` (defined here).
- module-initializer: set the _initial_ (overrideable) pkg resolver.
- wakeGlobalDir: directory used to (locally) store instantiated packages and
  modules. Default is `/wake/`.


### <span title="Not Implemented" style="color: #FF4136"><b><i>.config</i></b></span>

- `./PKG.libsonnet`: Defines the pkg, including files to include and
  dependencies. Must return a single function (see <a style="font-weight: bold; color: #FF4136" title="SPC-API.PKG" href="#SPC-API">SPC-api.pkg</a>).
- `PKG.meta`: defines the pre-pkg and pkg hashes. The downloaded pkg is
  validated against these values and they are used to identify the pkg.
  This also contains the version of `wake` used to create the pkg. This also
  includes the version of wake used to create this file, which is used for
  debugging purposes only.
- `_wake_/`: this directory is created automatically and must NOT exist. Can be
  overriden with the `outputsDir`.
- `.wake.jsonnet`: can be located in the `$base/.wake.jsonnet` file of any pkg.
  Is is a jsonnet file that must not contain any imports, since it is used
  for determining what files must be retrieved to determine the pkg metadata.
  If it does not exist, the defaults will be used.  It contains the following
  fields:
  - `pkgLib`: override the location of `PKG.libsonnet`
  - `pkgMeta: override the location of `PKG.meta`
  - `wakeDir`: override the location of `_wake_/`. Must be a local path with a
    single component.

### <span title="Not Implemented" style="color: #FF4136"><b><i>.outputs</i></b></span>

The `_wake_/` folder contains
- `container.json`: metadata around the container the pkg is executing within,
  such as platform information. Exists only in the exec container.
- `pkg.json` and `module.json`: the fully instantiated config manifest for a
  pkg and module, exists only in the exec container. This has all of the same
  fields and data that was returned in `PKG.jsonnet` except:
  - all `getPkg` calls are now `pkgId`, which can be resolved to paths with
    `pkgPaths.json`.
  - all `getModule` calls are now `moduleId`, which can be resolved to paths
    with `modulePaths.json`
  - all `file` objects are now paths to valid files or symlinks
  - the `exec` object will have all it's attributes expanded and files
    realized.
- `pkg-ready.json` and `module-ready.json`: the instantiated config manifest for a module/pkg.
  The same as `config.json` except the `file` objects are still `file` objects
  (but with pkgIds), since the paths have not been created in the build container.
- `pkgPaths.json`: a json file containing an object with key=pkgId, value=path.
  Exists only in the container (when paths exist).
  This file exists when a module is inside its execution container and the paths
  resolve to their corresponding pkg.
- `modulePaths.json`: a json file containing an object with key=moduleId, value=path.
  Exists only in the build container (when paths exist).
- `file.lock`: lockfile taken by the process that is processing the pkg. If no
  process has the lockfile and `state.json::state==unknown` then the folder
  will be deleted by the GC.
- `state.json`: json file containing pkg or module state. Includes:
  - `type`: one of [pkg, module]
  - `from`: the full metadata of how the pkg was retrieved. If a module, is
    `null`. This will be checked to make sure other pkgs don't try to retrieve
    the same pkg using a different pkg-retriever.
  - `state`: one of
    - unknown: unknown state, not ready.
    - pkg-meta: the pkg metadata exists in the folder.
    - pkg-retrieved: _all_ data has been retrieved, but required files and
      dependencies have not been linked,
    - pkg-done: all data has been retrieved and all pkg dependencies are done.
    - module-ready: all of the module's dependencies are done and the module is
      ready to be built in a container.
    - module-done: the module has been built and contains all declared outputs.
  - `inputsHash`: hash of the inputs, must match `PKG.meta::hash`.
  - `allHash`: contains a hash of all individual files, inputs and outputs,
     as well as a hash of all members. Used when validating module integrity
     and transfering modules over a network.

### <span title="Not Implemented" style="color: #FF4136"><b><i>.processing</i></b></span>
A processing folder exists in an (unspecified) location determined by
`pkg-retriever` and `pkg-initializer` (they can be separate places, traditionally
this is in `/tmp`).

When the download is complete (and `state.json` has been set), they return the
path, which gets passed to `pkg-initializer`. The resolver then moves the files to
the proper place in `pkgs`. Similarily, modules are set up here, and when
complete they are moved to `modules/`. Traditionally, this is backed by a
temporary filesystem.


