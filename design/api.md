# SPC-api
partof: REQ-purpose
###

Below are the different types/functions that make up the core API of wake.

Some special notes:

- files can only be defined in `files`. Any reference to a "file" in inputs or outputs
  (or anywhere) will simply be its raw data (json, string, etc).

## [[.pkgInfo]] `pkgInfo(...)`
This is the information that defines a package identifier. It results in an
object which is used as part of other types.

This object frequently gets converted to a string in the form
`name|version|namespace` and then an optional `|hash`.

Arguments:
- `name`: the name to give to the pkg. Must be at least 3 characters.
- `version`: semantic version used when resolving packages. Must be a valid
  semantic version requirement.
- `namespace=null`: a disambiguity between modules with the same name and
  version.  Used by organiations to control where modules come from. Must
  be at least 3 characters. `null` is treated as `""`

## [[.declarePkg]] `declarePkg(...)`

Arguments:
- `pkgInfo`
- `pkgDef=list[path]`: a list of paths to _local_ files which are necessary to
  define the `PKG.libsonnet` file. This should include all libsonnet files that
  any function defined in `PKG.libsonnet` might eventually import.
- `files=list[path]`: a list of paths to _local_ files to include. This automatically
  includes `PKG.libsonnet` itself and paths in `modules`, and is used to compute the hash of
  the PKG.libsonnet.  `inputs=function(wake, pkg) -> map`: function which takes in the
  instantiated `pkg` and returns a flat map of key/values. The values are
  _strongly typed_ and can include: ref, file.
- `pkgs`: flat map of key/pkgInfo. This is resolved first, and is used for
  finding and downloading pkgs.
- `modules=map[key, function]`: map of local modules of the pkg.
  `function(wake, pkg, config) -> moduleId`
- `exports=function(pkg) -> obj`: function which takes the completed pkg and
  returns jsonnet objects this pkg exports, for use by other (dependent) pkgs.
  This can be strings, integers, objects and even functions -- If gloabls are
  included, dependent pkgs must check the unresolved status with
  `wake.util.isCompleted` before attempting computation.
- `globals=list[key]`: global values this pkg depends on. Will be a key/value
  map
  in `state=pkg-completed`.
- `setGlobals=function(wake, pkg) -> list[[key, value]]`: set the global values which
  this pkg in `state=pkg-completed`. See the _Globals_ section below.

> Note: the function defined in `inputs` is called at the beginning of this
> pkg's instantiation, only after all the `pkgs` this pkg is dependent on are
> `state=done`.

### setGlobals
Global values are a _single key_ which are utilized by other pkgs
and modules for configuration purposes.

Global values are set from calling `pkgs::gloabls` immediately after the pkg
reaches `state=pkg-completed`. The pkg must have `PERMISSION_DEFINE_GLOBAL` or be
defined in `$WAKEPATH`. It is an error for two pkgs to attempt to set the
same global key.

Global values _must_ be one of the following types:
- `pkg` objects, used as dependencies. Common examples include compilers,
  programming languages, and "standard" libraries.
- `config` objects, which are themselves jsonnet objects. Common examples
  include opt-level settings, debug settings, testing configuration, etc.
- `exec` objects with `container=wake.ANY`. These are necessary to override the
  default `pkg-retriever` and `data-store` objects, but is also commonly used
  for defining global containers (i.e. `docker`).

Globals can be set by any file in `$WAKEPATH/`, as well as by any pkg that has
`PERMISSION_DEFINE_GLOBAL`. It is an error to attempt to set a global to a
different value.

When the `globals` function is called, its `wake` object is slightly altered
such that it cannot make calls to `getPkg` or `getModule`. It must therefore
set a global pkg via a reference from the `pkg` input.

## [[.getPkg]] `getPkg(...)`
Retrieve a pkg.

There are a million possible ways to retrieve a pkg. From a path
is the simplest (and most obvious), but pkgs can be stored anywhere
that computers are.

Wake takes no opinions on _how_ to retrieve pkgs. The `from`

Pkgs are _just data_ that can depend on other pkgs or the direct execution
of other pkgs (cannot depend on modules).

Arguments:
- `pkgInfo`
- `from`: one of:
  - ./path`: a reflike local directory where a `PKG.libsonnet` file exists.
  - `wake.exec(ePkg, ...)`: to execute another pkg to retrieve the pkg.
    Typically this is gotten from a `getGlobal` call.
- `permisions=null`: permissions to grant the pkg. `defineGlobal` is required
  for the retrieved pkg to _itself_ define globals.

Returns: pkgInfo with an exact version.


## [[.module]] `module(...)`

The definition of something to build.

Note that when `exec` is running it is within its `container` and has read
access to all files and inputs the local `pkg` the module is defined in, as
well as any pkgs and modules it is dependt on.

Also note that when the inputs and outputs functions are called, the `pkg` will
be _fully resolved_, meaning that `module.pkgs.foo` will return the full `pkg`
object, and all paths will be resolved (the same is true for
`module.modules.foo`.

When instantiating (i.e. building) the module, `exec` will then be passed the
fully instantiated manifest, meaning it is just JSON (no jsonnet functions, etc).

Arguments:
- `pkg`: the pkg this module came from.
- `modules`: dependencies of this module.
- `files=function(wake, module) -> list[reflike]`: function which returns additional
  files (on top of `pkg.files`) to create/link for this specific module.
  Possibly new links, dumped configs, or references to inputs/outputs from
  `modules`. Cannot specify any references that don't already exist (i.e.  new
  files), except `file(..., dump=true)`.
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


## [[.getModule]] `getModule(...)`
Retrieve a module from a pkg with a specified config.

This is how a module specifies its dependencies.

Arguments:
- `pkg`
- `module`
- `config`: either a raw config or a function which gets passed the module.

Returns: `module` object.

## [[.exec]] `exec(...)`
Specification for executing from within a pkg.

Arguments:
- `path`: local or linked path to execute
- `config`: config to pass to the executable as JSON via `stdin`
- `args`: list of strings to pass as arguments to the executable.
- `env`: environment variables to pass to the executable, resolved as strings.
  Consider using `config` instead.
  - all `file` objects will be converted to absolute paths `/full/path/to/file`
  - all raw strings will remain as strings
  - integers will be converted to a string (`MYINT=3`)
  - lists of strings are allowed, separated by `\n` characters.
  - !! values which serialize to be over 4kB will raise an error.
  - !! all other values will raise an error.
- `container`: an `exec` to use for where to execute. The specified
  must have `exec::container=wake.ANY`.

The `exec` object will be serialized within `module.json` or `pkg.json`
([[SPC-rc]]) and included as part of `module-ready` (see [[SPC-rc]]).  It is
the container's job to then properly execute it with all files and dependencies
made available (linked or mounted).

## [[.file]] `file(path, from=ref, dump=false)`
Refer to the file at `path`. If `from` is specified, will create a ln to a file
there using a file from another location (i.e. path, config blob, pkg or module).

If dump is `true`, `from` should refer to a config blob. The manifest of the
config will be converted to json and dumped at `path`.

Returns: `file` object

# SPC-helpers
These are helper functions are not part of the core types.

##  [[.dir]]: `dir(include, exclude=null)`
Path to a directory of files to glob-include.

All matching sub files and directories will be recursively included,
except those listed in `exclude`.

Returns: `List[path]`


## SPC-rc
The following files are default or required:

### [[.user]]
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
- pkg-retriever-initial: set the _initial_ (overrideable) pkg retriever when
  building.  The default one can only handle local paths.
- pkg-initializer-initial: set the _initial_ (overrideable) pkg resolver. The
  default one can only store pkgs in `wakeGlobalDir` (defined here).
- module-initializer: set the _initial_ (overrideable) pkg resolver.
- wakeStore: directory used to (locally) store instantiated packages and
  modules. Default is `/wake/`. Contains:
  - `pkgDefs`: local pkg definitions and symlinks.
  - `pkgs`: local partial or fully complete pkgs (data only, no links)
  - `modules`: local fully complete modules (data only, no links)
  - `store`: future directory of symlinked local modules, could be used to (for
    example) create a WakeOS.


### [[.config]]

- `PKG.libsonnet`: Defines the pkg, including files to include and
  dependencies. Must return a single function (see [[SPC-api.pkg]]).
- `PKG.meta`: defines the pre-pkg and pkg hashes. The downloaded pkg is
  validated against these values and they are used to identify the pkg.
  This also contains the version of `wake` used to create the pkg. This also
  includes the version of wake used to create this file, which is used for
  debugging purposes only.
- `.wake/`: this directory is created automatically and must NOT exist. Can be
  overriden with the `outputsDir`.
- `.wake.jsonnet`: can be located in the `$base/.wake.jsonnet` file of any pkg.
  Is is a jsonnet file that must not contain any imports, since it is used
  for determining what files must be retrieved to determine the pkg metadata.
  If it does not exist, the defaults will be used.  It contains the following
  fields:
  - `pkgLib`: override the location of `PKG.libsonnet`
  - `pkgMeta: override the location of `PKG.meta`
  - `wakeDir`: override the location of `.wake/`. Must be a local path with a
    single component.

### [[.outputs]]

The `.wake/` folder contains
- `pkg.json` and `module.json`: the fully instantiated config manifest for a
  pkg and module, exists only when the pkg is `pkg-complete` or ready to be
  builtin a container (respectively). This has all of the same fields and data
  that was returned in `PKG.jsonnet` except:
  - all `getPkg` calls are now full `pkgId`.
  - all `getModule` calls are now `moduleId`
  - all `file` objects are now paths to valid files or symlinks
  - the `exec` object will have all it's attributes expanded and files
    realized.
- `pkg-ready.json` and `module-ready.json`: the instantiated config manifest
  for a module/pkg. The same as `config.json` except the `file` objects are still `file` objects
  (but with pkgIds), since the paths have not been created in the build container.
- `pkgPaths.json`: a json file containing an object with key=pkgId, value=path.
  Exists only in the container (when paths exist).
  This file exists when a module is inside its execution container and the paths
  resolve to their corresponding pkg.
- `modulePaths.json`: a json file containing an object with key=moduleId, value=path.
  Exists only in the build container (when paths exist).
- `container.json`: metadata around the container the pkg is executing within,
  such as platform information. Exists only in the exec container.
- `file.lock`: lockfile taken by the process that is processing the pkg. If no
  process has the lockfile and `state.json::state==unknown` then the folder
  will be deleted by the GC.
- `state.json`: json file containing pkg or module state. Includes:
  - `type`: one of [pkg, module]
  - `from`: a _list_ of the full metadata of all the ways folks tried to
    retrieve the pkg using `getPkg`. Each attempt must check that the hashes
    remain identical.
  - `state`: one of
    - unknown: unknown state, not ready.
    - pkg-def: the pkgDef files have all been retrieved and validated.
    - pkg-retrieved: _all_ data has been retrieved, but required files and
      dependencies have not been linked,
    - pkg-completed: all data has been retrieved and all pkg dependencies are done.
    - module-ready: all of the module's dependencies are done and the module is
      ready to be built in a container.
    - module-completed: the module has been built and contains all declared outputs.
  - `inputsHash`: hash of the inputs, must match `PKG.meta::hash`.
  - `allHash`: contains a hash of all individual files, inputs and outputs,
     as well as a hash of all members. Used when validating module integrity
     and transfering modules over a network.

Special files:
- `getPkg.json`: only exists when executing a `getPkg` call. Contains the json
  manifest of the `getJson` call.


### [[.processing]]
A processing folder exists in an (unspecified) location determined by
`pkg-retriever` and `pkg-initializer` (they can be separate places, traditionally
this is in `/tmp`).

When the download is complete (and `state.json` has been set), they return the
path, which gets passed to `pkg-initializer`. The resolver then moves the files to
the proper place in `pkgs`. Similarily, modules are set up here, and when
complete they are moved to `modules/`. Traditionally, this is backed by a
temporary filesystem.
