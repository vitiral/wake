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
  These states are `declared` -> `defined` -> `ready`.
  - Closures on the pkg (like `exports`) are called when the pkg has achieved a state.
    The state is demarked with the name of the input, i.e. `pkgDefined`
- Modules are of type `function(wake, pkgReady, config)` and return a call to
  `wake.defineModule`. Modules define what is built and how it is built.
  - Modules are hashed as the pkg (just data) the `config` passed to them, and
    finally the modules they depend on.


- [[.pkgId]]: the uniq id (including exact version and hash) of a specific
  pkg. Used for pkg lookup.
- [[.pkgReq]]: defines a semver requirement for a `getPkg` call to retreive.
- [[.getPkg]]: retrieve a pkg lazily.
- [[.declarePkg]]: declare a pkg.
- [[.declareModule]]: declare how to build something with a pkg.
- [[.fsentry]]: specify a file-system object within a pkg or module.
- [[.exec]]: a declared executable. Is typically a member of `module.exec`
  or can be a member of `exports` for a pkg or module.


# SPC-eval


# SPC-lib-eval



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
