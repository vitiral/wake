# SPC-api
<details>
<summary><b>metadata</b></summary>
<b>partof:</b><br>
<li><a style="font-weight: bold; color: #FF4136" title="SPC-ARCH" href="#SPC-ARCH">SPC-arch</a></li>
<b>parts:</b> <i>none</i></a><br>
<b>file:</b> design/api.md<br>
<b>impl:</b> <i>not implemented</i><br>
<b>spc:</b>87.50&nbsp;&nbsp;<b>tst:</b>0.00<br>
<hr>
</details>


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


- <span title="/home/rett/open/wake/wake/lib/wake.libsonnet[4]" style="color: #0074D9"><b><i>.pkgId</i></b></span>: the uniq id (including exact version and hash) of a specific
  pkg. Used for pkg lookup.
- <span title="/home/rett/open/wake/wake/lib/wake.libsonnet[16]" style="color: #0074D9"><b><i>.pkgReq</i></b></span>: defines a semver requirement for a `getPkg` call to retreive.
- <span title="/home/rett/open/wake/wake/lib/wake.libsonnet[55]" style="color: #0074D9"><b><i>.getPkg</i></b></span>: retrieve a pkg lazily.
- <span title="/home/rett/open/wake/wake/lib/wake.libsonnet[74]" style="color: #0074D9"><b><i>.declarePkg</i></b></span>: declare a pkg.
- <span title="/home/rett/open/wake/wake/lib/wake.libsonnet[153]" style="color: #0074D9"><b><i>.declareModule</i></b></span>: declare how to build something with a pkg.
- <span title="/home/rett/open/wake/wake/lib/wake.libsonnet[189]" style="color: #0074D9"><b><i>.fsentry</i></b></span>: specify a file-system object within a pkg or module.
- <span title="/home/rett/open/wake/wake/lib/wake.libsonnet[224]" style="color: #0074D9"><b><i>.exec</i></b></span>: a declared executable. Is typically a member of `module.exec`
  or can be a member of `exports` for a pkg or module.


# SPC-arch
<details>
<summary><b>metadata</b></summary>
<b>partof:</b> <i>none</i></a><br>
<b>parts:</b><br>
<li><a style="font-weight: bold; color: #FF851B" title="SPC-API" href="#SPC-API">SPC-api</a></li>
<b>file:</b> design/arch.md<br>
<b>impl:</b> <i>not implemented</i><br>
<b>spc:</b>4.90&nbsp;&nbsp;<b>tst:</b>0.00<br>
<hr>
</details>

The implementation for the wake pkg manager and build system is split into two
completely distinct pieces:

- <a style="font-weight: bold; color: #FF851B" title="SPC-API" href="#SPC-API">SPC-api</a>: the "wake.libsonnet" library, which is a pure jsonnet library
  that provides the user interface within `PKG.libsonnet` files and its
  dependencies.
- <a style="font-weight: bold; color: #FF4136" title="SPC-EVAL" href="#SPC-EVAL">SPC-eval</a>: the wake "evaluation engine", which is a cmdline frontend that
  injests files and executes the steps necessary to evaluate local hashes,
  retrieve pkg dependencies, and execute `exec` objects in order to complete
  modules.


## <span title="Not Implemented" style="color: #FF4136"><b><i>.state</i></b></span>
These two pieces work together by the evaluation engine executing the jsonnet
configuration within `cycles`, moving the state of wake objects through
the following flow. States are always in _italics_ within this documentation.
- _undefined_: the object is _declared_ as a dependency, but it has not yet
  been _declared_.
- _declared_: the object's _declaration_ has been retrieved, but not all of its
  dependencies have been _defined_.
- _defined_: the object has ben _declared_ and all of its dependencies have been
  _defined_.
- _ready_: (modules only) all of a module's dependencies have been _completed_.
  The module is ready to be executed and _completed_.
- _completed_:
  - for `pkg`: the pkg is fully downloaded and in the **store**.
  - for `module`: `module.exec` has been executed (built) and the data is in
    the **store**.


## Overrides
These are the overrides available to users to change wake's behavior in various
phases (<a style="font-style: italic; color: #B10DC9" title="SPC-PHASE not found" >SPC-phase</a>). All of these objects are `exec` objects who's `args`
and `config` are both set to `null` (they will be overriden), and who's
`container=wake.LOCAL`.

### <span title="Not Implemented" style="color: #FF4136"><b><i>.wakeStoreOverride</i></b></span>: Override where to store artifacts

`root.pkgs.wakeStoreOverride` can be (optionally) set to an `exec` who's `config=null`.

The **wakeStoreOverride** is passed to every **container** and must be
supported by all containers. A good example would be a distributed filesystem
which all types of containers (and the user's computer) use to mount the
required fsentries for building modules.

These are the following `config` objects the **wakeStoreOverride** must handle:
- `{F_TYPE:T_STORE_READ, pkgId: <pkgId>, moduleId: <moduleId>}`: the **store** must
  return the _path_ to the given `pkgId` or `moduleId` with all of its local fsentries
  properly created/linked, or an empty string if no such object exists. This is
  used both:
  - To check if a pkg or module exists before retrieving or building it.
  - To create the fsentries for building a module within a container. The
    path must therefore have the characteristic that all files within it are
    copy-on-write (since the module may mutate them).
- `{F_TYPE:T_STORE_TMP}`: the **store** must return a local filesystem _path_ to
  a directory where files can be retrieved, or an empty string if the system
  default should be used. This is used as a place to put files, so that later
  storing  them is more performant then re-sending them over the network.
- `{F_TYPE:T_STORE_CREATE, dir: <pkg-dir>, pkgId: <pkgId>, moduleId:
  <moduleId>}`: the store is passed a directory to an _completed_ pkg or module
  and it must put it in the store.

### <span title="Not Implemented" style="color: #FF4136"><b><i>.wakeCredentialsOverride</i></b></span>: Override how credentials are retrieved
This is currently poorly defined, but the basic idea is:

- User defines hashed credentials is `$WAKEPATH/user.jsonnet`. This could
  also be re-generated every time `wake build` is run.
- **wakeCredentialsOverride** is called with these credentials and the
  container environment to generate LST.

Something like that... more design is necessary.


### <span title="Not Implemented" style="color: #FF4136"><b><i>.wakeGetPkgOverride</i></b></span>

If an `exec` is specified as the in a <a style="font-weight: bold; color: #FF851B" title="SPC-API.GETPKG" href="#SPC-API">SPC-api.getPkg</a> call, then it will be
used to retrieve the pkg specified. The `exec` must adhere to the following
API, where:

- `dir` is a path to a (local) temporary directory to store the files. (Note
  that this directory can be a link to a distributed fileystem.)
- `definitionOnly` is a bool regarding whether to retrieve only the
  `fsentriesDef` or the full `fsentries`.
- `..getPkg` is the `getPkg` arguments flattened

```
{
    F_TYPE:T_GET_PKG,
    dir: <tmpDir>,
    definitionOnly: bool,
    ..getPkg
}
```

It must then return `rc=0` and have the pkg retrieved within the `dir` passed to it.

If the pkg has a <span title="Not Implemented" style="color: #FF4136"><b><i>.localDependenciesFile</i></b></span> then it must also retrieve the
required dependencies and put them in the directories specified in that file.


## Store
The **store** (always in bold) has a presentation API to both the libsonnet and
eval engines:

- <span title="Not Implemented" style="color: #FF4136"><b><i>.wakeStoreSonnet</i></b></span>: For `wake.libsonnet` API, the **store** appears as the
  <a style="font-weight: bold; color: #FF851B" title="SPC-API.GETPKG" href="#SPC-API">SPC-api.getPkg</a> API, which lazily retrieves pkgs.
- eval: for the evaluation engine, there are multiple aspects
  of the **store** depending on the **phase**.
  - <span title="Not Implemented" style="color: #FF4136"><b><i>.wakeStoreLocal</i></b></span>: in <a style="font-style: italic; color: #B10DC9" title="SPC-PHASE not found" >SPC-phase</a>, the **store** is always
    a local file directory (pkg definitions should always be very small),
    although an arbitrary retriever can get them.
  - <span title="Not Implemented" style="color: #FF4136"><b><i>.wakeStoreModule</i></b></span>: in <a style="font-style: italic; color: #B10DC9" title="SPC-PHASE not found" >SPC-phase</a>, the **store** can be
    either the local filesystem, or overriden with <a style="font-weight: bold; color: #FF4136" title="SPC-ARCH.WAKESTOREOVERRIDE" href="#SPC-ARCH">SPC-arch.wakeStoreOverride</a>.


## Phases
There are only two phases to wake execution:

- <span title="Not Implemented" style="color: #FF4136"><b><i>.phasePkgComplete</i></b></span>: where pkgs are retrieved and put in the
  <a style="font-weight: bold; color: #FF4136" title="SPC-ARCH.WAKESTORELOCAL" href="#SPC-ARCH">SPC-arch.wakeStoreLocal</a>. This can run multiple cycles until all pkgs
  are resolved and the proper dependency tree is determined.
- <span title="Not Implemented" style="color: #FF4136"><b><i>.phaseModuleComplete</i></b></span>: all pkgs have been retrieved and configuration calculated
  in the pure jsonnet manifest. The `exec` objects are then executed within
  their `container` in the proper build order with the proper links to their
  dependent pkgs and modules.

Note that by the end of **phasePkgCompete** all pkgs _and_ modules have been
fully _defined_, and no more jsonnet needs to be evaluated.

When modules are being built, they are given only the manifested **json**, not
jsonnet objects. So jsonnet functions remain only as configuration utilities,
whereas module inputs remain only pure data.

## Special Files and Directories

- <span title="Not Implemented" style="color: #FF4136"><b><i>.pkgFile</i></b></span> `./PKG.libsonnet` file which contains the call to <a style="font-weight: bold; color: #FF851B" title="SPC-API.DECLAREPKG" href="#SPC-API">SPC-api.declarePkg</a>
- <span title="Not Implemented" style="color: #FF4136"><b><i>.wakeDir</i></b></span> `./.wake/`: reserved directory for containing wake metadata. Should
  not be used by users. Can contain the following fsentries:
  - <span title="Not Implemented" style="color: #FF4136"><b><i>.pkgsLibFile</i></b></span>:  `pkgs.libsonnet` file containing the imports to already
    defined pkgs. This is regenerated each cycle in the **phasePkgComplete**
    with the currently known pkgs.
  - <span title="Not Implemented" style="color: #FF4136"><b><i>.runFile</i></b></span>: `run.jsonnet` which is used for executing each cycle. Essentially
    each cycle is a call to `jsonnet .wake/run.jsonnet`, with the `pkgsLibFile`
    updated each time.
  - <span title="Not Implemented" style="color: #FF4136"><b><i>.fingerprintFile</i></b></span>: `fingerprint.json` file which is auto-generated by
    the build system for local pkgs, and required to match the cryptographic
    hash for retrieved pkgs or modules. This can also contain other
    non-hashable data like the signature of the fingerprint hash.
  - <span title="Not Implemented" style="color: #FF4136"><b><i>.localStoreDir</i></b></span>: `localStore/` directory containing only _local_ pkg
    definitions. Used for pkg overrides.
  - <span title="Not Implemented" style="color: #FF4136"><b><i>.localDependenciesFile</i></b></span>: `localDependencies.json` file containing a map of
    `path: pkgId`. This is automatically generated when building local
    dependencies and is used to retrieve "locked" dependencies of external
    depdendencies.


## Appendixes
These are a few "risks of the current architecture.

### Appendix A: Consideration of version changes as cycles progress
There is a possible issue in what happens during pkg resolution. Ideally we would
retrieve aas _few_ pkgs as possible to meet all semver requirements. This ideal
is difficult to implement, and is itself an NP-hard problem. The problem is
particularily difficult when the package requirements and quanity can change
every cycle (as they can here).

Let's say we had the following cycles:

- pkg-local requires pkg a(>=1.0), a(1.3 - 2.0), b(1.0 - 2.3)
- cycle A: we end up with a(2.0), b(3.0)
  - pkg-a(2.0) requires b(1.0 - 1.8)
- cycle B: we end up with a(2.0), b(1.8)
  - **notice that b changed**

One can imagine this cycle continuing for a very long time. The key to success
here are multiple points:
- Recall that pkgs are not built, and it is illegal to switch exec's for the same
  (name, namespace) pair. Therefore although pkgs, can ask for different pkgs, they
  cannot use _different exec_'s to do so.
- graph-cycles in the pkg graph are never allowed. Because of this, it should be not
  possible to create a graph-cycle between evaluation cycles (TODO: not proven).
- It is the job of the `exec` retrievers to simply return the pkg that _best
  matches that requirement_. It should not worry about other pkgs that have
  been retrieved.
- All "best packages" dependency trees must be resolved before full pkg
  download
  and module instantiation.

Also note that the metadata downloaded per-pkg is very small in this stage --
it should only include the files in `pkgFiles` except for the smallest of
packages. Therefore constructing the tree is relatively cheap, even over the
internet.


# SPC-eval
<details>
<summary><b>metadata</b></summary>
<b>partof:</b> <i>none</i></a><br>
<b>parts:</b> <i>none</i></a><br>
<b>file:</b> design/api.md<br>
<b>impl:</b> <i>not implemented</i><br>
<b>spc:</b>0.00&nbsp;&nbsp;<b>tst:</b>0.00<br>
<hr>
</details>



# SPC-lib-eval
<details>
<summary><b>metadata</b></summary>
<b>partof:</b> <i>none</i></a><br>
<b>parts:</b> <i>none</i></a><br>
<b>file:</b> design/api.md<br>
<b>impl:</b> <i>not implemented</i><br>
<b>spc:</b>0.00&nbsp;&nbsp;<b>tst:</b>0.00<br>
<hr>
</details>




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


### <span title="Not Implemented" style="color: #FF4136"><b><i>.config</i></b></span>

- `PKG.libsonnet`: Defines the pkg, including files to include and
  dependencies. Must return a single function (see <a style="font-style: italic; color: #B10DC9" title="SPC-API.PKG not found" >SPC-api.pkg</a>).
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

### <span title="Not Implemented" style="color: #FF4136"><b><i>.outputs</i></b></span>

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


### <span title="Not Implemented" style="color: #FF4136"><b><i>.processing</i></b></span>
A processing folder exists in an (unspecified) location determined by
`pkg-retriever` and `pkg-initializer` (they can be separate places, traditionally
this is in `/tmp`).

When the download is complete (and `state.json` has been set), they return the
path, which gets passed to `pkg-initializer`. The resolver then moves the files to
the proper place in `pkgs`. Similarily, modules are set up here, and when
complete they are moved to `modules/`. Traditionally, this is backed by a
temporary filesystem.


