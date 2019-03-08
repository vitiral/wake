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
- _undefined_: the object is a dependency in a _declared_ pkg or module.
- _declared_: the object's _declaration_ has been retrieved, but not all of its
  dependencies have been _defined_.
- _defined_: the object has ben _declared_ and all of its dependencies have been
  _defined_.
- _ready_: (modules only) all of a module's dependencies have been _completed_.
  The module is ready to be executed and _completed_.
- _completed_:
  - for `pkg`: the pkg and all dependencies are fully downloaded and in the
    **store**.
  - for `module`: `module.exec` has been executed (built) and the data is in
    the **store**.


## Overrides
These are the overrides available to users to change wake's behavior in various
phases ([[SPC-phase]]). All of these objects are `exec` objects who's `args`
and `config` are both set to `null` (they will be overriden), and who's
`container=wake.LOCAL`.

### [[.wakeStoreOverride]]: Override where to store completed objects

`root.pkgs.wakeStoreOverride` can be (optionally) set to an `exec` who's `config=null`.

The **wakeStoreOverride** is passed to every **container** and must be
supported by all containers. A good example would be a distributed filesystem
which all types of containers (and the user's computer) use to mount the
required fsentries for building modules.

These are the following `config` objects the **wakeStoreOverride** must handle:
- `{F_TYPE:T_STORE_READ, pkgIds: <pkgIds>, moduleIds: <moduleIds>}`: the
  **store** must return a json blob with keys `pkgs` and `modules`, each containing
  objects with key=id, value=absolute-path to the given completed pkg or module,
  or null if no such pkg or module exists. It is recommended that all paths are
  permission of read-only.
- `{F_TYPE:T_STORE_TMP}`: the **store** must return a local filesystem _path_ to
  a directory where files can be retrieved, or an empty string if the system
  default should be used. This is used as a place to put files, so that later
  storing  them is more performant then re-sending them over the network.
- `{F_TYPE:T_STORE_CREATE, dir: <dir>, pkgId: <pkgId or null>`
    `, moduleId: <moduleId or null>}`: the store is passed a directory to a
    _completed_ pkg or module and it must put it in the store.

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
API, whereby a file will be put at `./getPkg.json` containing the following
information. Any downloaded pkgs should be put in `./retrieved/`, with
directories named the `pkgId`.


## `T_GET_PKGS`

- `dir` is a path to a (local) temporary directory to put the files.
- `definitionOnly` is a bool regarding whether to retrieve only the
  `fsentriesDef` or the full `fsentries`. It is up to the retriever whether
  to follow this rule (some source code is so small it is better to retrieve
  the full pkg)
- `pkgVersions`: is a list of pkgs of the form `["name(namespace)(=1.3.2)"]`. Note
  that only exact versions will ever be retrieved by `T_GET_PKGS`
- `pkgExists`: is a list of existing pkgIds (so they are not re-retrieved).

```
{
    F_TYPE:T_GET_PKG,
    dir: <tmpDir>,
    definitionOnly: bool,
    pkgVersions: <list-of-pkgVersion strings>
}
```

If the pkg has a [[.localDependenciesFile]] then it must also retrieve the
required dependencies and put them in the directories specified in that file.

## `T_GET_CANDIDATES`

```jsonnet
{
    F_TYPE:T_GET_CANDIDATES,
    pkgReqs: <list of pkg requiremnts>,
    known: list[pkgKey],
}
```

- `pkgReqs` is a list of pkg reqs of the form `["name(namespace)(>=1.2,<=3)"]`.
  Note: all semverReq will be of the form `(min,max)`.

The retriever should return a list of possible candidates. The list should have
items of the form:

```
{
    pkgVer: <version>,
    pkgs: [pkgReq],
}
```


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
  - `pkgs.libsonnet` file containing the imports to already
    defined pkgs. This is regenerated each cycle in the **phasePkgComplete**
    with the currently known pkgs.
  - `run.jsonnet` which is used for executing each cycle. Essentially
    each cycle is a call to `jsonnet .wake/run.jsonnet`, with the `pkgsLibFile`
    updated each time.
  - `fingerprint.json` file which is auto-generated by
    the build system for local pkgs, and required to match the cryptographic
    hash for retrieved pkgs or modules. This can also contain other
    non-hashable data like the signature of the fingerprint hash.
  - `localStore/` directory containing only _local_ pkg
    definitions. Used for pkg overrides.
  - `localDependencies.json` file containing a map of
    `path: pkgId`. This is automatically generated when building local
    dependencies and is used to retrieve "locked" dependencies of external
    depdendencies.


## Appendixes
These are a few "risks of the current architecture.

### Appendix A: Consideration of version retrieval
There are a few known facts that are important about version retrieval:

- When retrieving pkgs, the retriever is allowed to return as many
  pkgDefinitions as it wants.
  - Generally it should return only a sampling. It will be given opportunities
    to retrieve more once the reqs have been narrowed.
- Executing `PKG.libsonnet` with no dependencies available (along with the
  local path dependencies) is sufficient to obtain its _static dependencies_.
- A flat map can then be created of all dependencies, by retrieving all of
  their definitions.

For example, these are the pkgs to solve:

- pkgA(2.3) requries pkgB(>1.0), pkgE(>=1.0, <3.0)
- pkgB(1.2 requires pkgE(>=1.2, <2.0)

We retrieve some pkgs and create a flat map which specifies which pkgs have
which requirements.

```python
pkgsReqs = {
    "pkgA(2.3)": [
        "pkgB(>1.0)"
        "pkgE(>=1,0,<3.0)"
    ],
    "pkgB(1.2)": [
        "pkgE(>=1.2, <2.0)"
    ],
    "pkgE(1.0)": [],
    "pkgE(1.1)": [],
    "pkgE(1.2)": [],
    ...
    "pkgE(1.9)": [],
}
```

We then create a hashmap of pkgs with OrderedSets of all the versions available

```python
pkgsAvailable = {
    pkgA: [2.3],
    pkgB: [1.2],
    pkgE: [1.0, 1.1, 1.2, ..., 1.9],
}

def choose_latest(req):
    pkgKey = req.pkgKey()  # i.e. pkgB(>2.0) -> pkgB
    for available in pkgsAvailable[pkgKey].reverse():
        if req.matches(available):
            return available
    return None
```

There is now one more step. We reduce all reqs down to groups by joining them
all together.

```python
def construct_req_muts():
    req_muts = {}  # Map[pkgKey, set[req]]

    for pkgId, reqs in pkgsReqs:
        for req in reqs:
            reqKey = req.key()
            req_mut = req_muts.get(reqKey)
            if req_mut is None:
                req_mut = ReqMut()

            req_mut.extend_constraints(req)

    return req_muts

req_muts = construct_req_muts()
```

ReqMut calls `.finalize()` to become ReqFinal. ReqFinal is an object which
contains a list of only `ReqRange` objects, representing all of the
non-overlapping "groups" that need to be solved for.

ReqRange(min, max)
- the min and max can both be None.
- the min and max can be inclusive or exclusive.
- if min(inclusive)==max(exclusive) it is an exact version.

We have now constructed a map of objects `Map[PkgKey, FinalReq]`.
We just need to feed the pkgsAvailable to it and we will have
PkgChoices objects. We then walk through the `pkgsReqs` to choose
the dependencies of each pkg and write it to `pkgsImport.libsonnet`


### Appendix B: Consideration of version changes as cycles progress
There is a possible issue in what happens during pkg resolution. Ideally we would
retrieve aas _few_ pkgs as possible to meet all semver requirements. This ideal
is difficult to implement, and is itself an NP-hard problem. The problem is
particularily difficult when the package requirements and quanity can change
every cycle (as they can here).

Let's say we had the following cycles:

- pkg-local requires pkg a(>=1.0), a(1.3 - 2.0), b(1.0 - 2.3)
- cycle A: we end up with a(2.0), b(2.3)
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


### Appendix C: Outputs considerations
> This section is still in early concept phase.

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
