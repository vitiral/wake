# SPC-arch
The implementation for the wake pkg manager and build system is split into two
completely distinct pieces:

- [[SPC-api]]: the "wake.libsonnet" library, which is a pure jsonnet library
  that provides the user interface within `PKG.libsonnet` files and its
  dependencies.
- [[SPC-eval]]: the wake "evaluation engine", which is a cmdline frontend that
  injests files and executes the steps necessary to evaluate local hashes,
  retrieve pkg dependencies, and execute `exec` objects in order to complete
  modules.


## [[.state]]
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
phases ([[SPC-phase]]). All of these objects are `exec` objects who's `args`
and `config` are both set to `null` (they will be overriden), and who's
`container=wake.LOCAL`.

### [[.wakeStoreOverride]]: Override where to store artifacts

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

### [[.wakeCredentialsOverride]]: Override how credentials are retrieved
This is currently poorly defined, but the basic idea is:

- User defines hashed credentials is `$WAKEPATH/user.jsonnet`. This could
  also be re-generated every time `wake build` is run.
- **wakeCredentialsOverride** is called with these credentials and the
  container environment to generate LST.

Something like that... more design is necessary.


### [[.wakeGetPkgOverride]]

If an `exec` is specified as the in a [[SPC-api.getPkg]] call, then it will be
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

If the pkg has a [[.localDependenciesFile]] then it must also retrieve the
required dependencies and put them in the directories specified in that file.


## [[.store]] Store
The **store** (always in bold) has a presentation API to both the libsonnet and
eval engines:

- [[.wakeStoreSonnet]]: For `wake.libsonnet` API, the **store** appears as the
  [[SPC-api.getPkg]] API, which lazily retrieves pkgs.
- eval: for the evaluation engine, there are multiple stages of the **store**
  depending on the **phase**.
  - In [[SPC-arch.phaseLocal]] and [[SPC-arch.phasePkgComplete]] the store is always
    the local filesystem who's behavior is defined by the wake CLI.
  - In [[SPC-arch.phaseModuleComplete]]: the **store** can be either the local
    filesystem, or overriden with [[SPC-arch.wakeStoreOverride]].


## Phases
There are only three phases to wake execution:

- [[.phaseLocal]]: where the local pkg's hashes are calculated and exported
  into `.wake/fingerprint.json`, then put into [[SPC-arch.wakeStoreLocal]]
- [[.phasePkgComplete]]: where pkgs are retrieved and put in the
  [[SPC-arch.wakeStoreLocal]]. This can run multiple cycles until all pkgs
  are resolved and the proper dependency tree is determined.
- [[.phaseModuleComplete]]: all pkgs have been retrieved and configuration calculated
  in the pure jsonnet manifest. The `exec` objects are then executed within
  their `container` in the proper build order with the proper links to their
  dependent pkgs and modules.

Note that by the end of **phasePkgCompete** all pkgs _and_ modules have been
fully _defined_, and no more jsonnet needs to be evaluated.

When modules are being built, they are given only the manifested **json**, not
jsonnet objects. So jsonnet functions remain only as configuration utilities,
whereas module inputs remain only pure data.

## Special Files and Directories

- [[.pkgFile]] `./PKG.libsonnet` file which contains the call to [[SPC-api.declarePkg]]
- [[.wakeDir]] `./.wake/`: reserved directory for containing wake metadata. Should
  not be used by users. Can contain the following fsentries:
  - [[.pkgsFile]]:  `pkgs.libsonnet` file containing the imports to already
    defined pkgs. This is regenerated each cycle in the **phasePkgComplete**
    with the currently known pkgs.
  - [[.runFile]]: `run.jsonnet` which is used for executing each cycle. Essentially
    each cycle is a call to `jsonnet .wake/run.jsonnet`, with the `pkgsLibFile`
    updated each time.
  - [[.fingerprintFile]]: `fingerprint.json` file which is auto-generated by
    the build system for local pkgs, and required to match the cryptographic
    hash for retrieved pkgs or modules. This can also contain other
    non-hashable data like the signature of the fingerprint hash.
  - [[.localStoreDir]]: `localStore/` directory containing only _local_ pkg
    definitions. Used for pkg overrides.
  - [[.localDependenciesFile]]: `localDependencies.json` file containing a map of
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
