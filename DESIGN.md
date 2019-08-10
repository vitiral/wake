```yaml @
artifact:
    code_paths:
      - wake/
```

# Types (SPC-type) <a id="SPC-type" />

**Package Identifiers**: the following are keys for looking up or specifying packages in various
ways. They are all strings, with components separated by `@`. The reason they are strings is
so they can be used as JSON keys as well as as file names. The following symbols are not allowed
within the components: `@\/`

- **pkgName** (`"{namespace}@{name}"`): Gives a human readable identifer on
  where to find the package. This is rarely used directly within the system
  except as part of other `pkg*` identifiers.
- **pkgReq** (`"{pkgName}@{requirements}"`): specifies what versions of a
  package are required as a dependency. `requirements` must be a [semver]
  compatible string.
- **pkgVer** (`"{pkgName}@{version}@{hash}"`): a single version of a package, including
  it's full name and hash.
- **pkgPath** (`"{storePkgPath}/{pkgVer}"`): a usable path to the package accessible on
  the "local" filesystem of the process.

**Module Identifiers**: unlike packages, modules can only be specified by their
exact version _and hash_. Note that the hash can change as the module's dependencies
can change even for a single version.

- **modHash**: (`"{modname}@{modhash}"`): an exact module identifier from
  within a package.
- **modVer**: (`"{pkgVer}@{modHash}"`): an exact module identifier, detailing
  the package it came from and the name of the module (`mod`) within the
  package.
- **modPath** (`"{storeModPath}/{pkgVer}/{modHash}"`): a usable path to the
  module accessible on the "local" filesystem of the process.

**NotFound**: used by the wakestore to return objects that were not found
- type: `NOT_FOUND`
- pkgVer: (if a package wasn't found) the package that wasn't found
- modVer: (if a module wasn't found) the module that wasn't found

**pkgInfo**: specifies a package's requested or resolved dependency tree. When
returned from the Package Manager all values will be defined as a single
`pkgVer`.
- pkgName: the name of the package
- pkgVer: (optional) the exact package version
- deps: _defined_ `wake.deps` object (globals and local deps are manifested).
  The values can either be **pkgReq** or **pkgInfo** objects.

**signature**: supports multiple types of cryptographic signature for signing
packages (TODO).

**pkgRemote**: a map of `pkgVer: remoteLocation`, where `remoteLocation` is an
unspecified blob of data. This is used soley within the Package Manager for
specifying how packages are retrieved.

**pkgOrigin**: a package origin.
- `pkgVer`: exact name and version of package
- `author`: the author of the package.
- `license`: the license string of the package.
- `website`: website of the package.
- `issues`: link where to report bugs for the package.

```
    "T_OBJECT": "object",
    "T_PKG": "pkg",
    "T_GET_EXPORT": "getExport",
    "T_MODULE": "module",
    "T_PATH_REF_PKG": "pathRefPkg",
    "T_PATH_REF_MODULE": "pathRefModule",
    "T_EXEC": "exec",

    "S_UNRESOLVED": "unresolved",
    "S_DECLARED": "declared",
    "S_DEFINED": "defined",
    "S_COMPLETED": "completed",

    "M_READ_PKGS": "readPkgs",
    "M_READ_PKGS_REQ": "readPkgsReq",

    "DIR_WAKE": ".wake",
    "DIR_LOCAL_STORE": "localStore",
    "DIR_RETRIEVED": "retrieved",

    "FILE_PKG": "PKG.libsonnet",
    "FILE_RUN": "run.jsonnet",
    "FILE_PKGS": "pkgs.libsonnet",
    "FILE_EXEC": "exec.json",

    "FILE_FINGERPRINT": "fingerprint.json",
    "FILE_LOCAL_DEPENDENCIES": "localDependencies.json",

    "EXEC_LOCAL": "execLocal"
```



# Wake Architecture (SPC-arch) <a id="SPC-arch" />

Wake has multiple pieces:

- The **wake.libsonnet** jsonnet library, which is how users write wake packages and
  contains functions and values for constructing and using wake types.

- The **wake cmdline** utility, which manages the build process through the various stages of
  execution.

- The [Package Manager] which is a cmdline utility which is called by the **wake
  cmdline**. It's job is to solve the dependency graph and retrieve packages
  from the internet (or elsewhere).

- The [Store] which handles storing data (packages and modules) so they
  can (seemingly) be accessed locally within an `exec`'s `container`.

- The [Credentials Manager] which handles credentials for the package manager
  and store.


## Package State
**Package** and **module** objects can have different states, which represent
different amounts of completeness. The **wake cmdline** manages moving objects
through these states via discovery, retrieval and execution of packages.

- _undefined_: the object is a dependency in a _declared_ pkg or module.
- _declared_: the object's _declaration_ has been retrieved, but not all of its
  dependencies have been _defined_.
- _defined_: the object has ben _declared_ and all of its dependencies have been
  _defined_.
- _ready_: (modules only) all of a module's dependencies have been _completed_.
  The module is ready to be executed and _completed_.
- _completed_:
  - for `pkg`: the pkg and all dependencies are fully downloaded and in the
    [Store].
  - for `module`: `module.exec` has been executed (built) and the data is in
    the [Store].


# Package Manager: Override how packages are obtained
# (SPC-packageManager) <a id="SPC-packageManager" />
```yaml @
partof:
- SPC-arch
```

There can only be a single Package Manager used within a wake execution, which
may (internally) farm it's work out to other language-specific Package Managers.

A package is specified by a `pkgReq` (see [SPC-type]). The Package Manager
handles resolving all requirements into the appropriate package graph.

The package manager is specified by `root.packageManager` and must support
the following [JSH] API.

## resolvePkgs method

Input Params:
- **pkgInfo**: the manifested root package requirements (i.e. globals
  resolved).
- **locked**: this is a map of `pkgName: pkgReq` objects. This is used to
  prevent unsecure packages from being included (which the Package Manager may
  also take care of by itself) as well as enabling "freezing" local application
  builds for the purpose of usability or debugging. The Package Manager must
  merge any use of these packages.
- **signatures**: these are used for signing packages for trust. They are an
  object of `pkgName: signature` where `signature` is the **signature** object.
  Every package used must have a signature, although this process is typically
  integrated with the Package Manager via the `getSignatures` method, a user
  can also specify them explicitly.
- **credentials**: this is unspecified object that the pkgManager should
  understand and can be used for verifying that the user has appropriate access
  to the package or can be used for tracking/billing usage of the package
  manager. It was obtained by calling the `overrideCredentials` exec on the
  root package, but is passed to the packageManager as a JSON object.


Outputs:
- **info**: a _fully defined_ **pkgInfo** object which specifies the complete
  graph of package dependencies. There should be only `pkgVer` objects.
- **remote**: map of `pkgVer: pkgRemote` specifying how to retrieve the
  packages using **readPkg**.

The resolvePkgs method must do the heavy lifting of resolving dependencies
within all packages.  Given a list of `pkgReqs` it must determine the specific
`pkgVer` of all root packages (given by `pkgReqs`) and **all** of their
recursive dependencies such that the result can be theoretically built.

To do this, the Package Manager must solve the dependency heiarchy for the
specific use-case of every package. In some cases (i.e.  python), this means
that there might be restrictions on the number of versions of each package
within a **dependency group**, which is defined as the recursive build
dependencies of any package.

To help determine this isolation, `wake.deps` allows for specifying several
levels of restrictions on dependencies:

- **unrestricted**: these are dependencies with no version restrictions, meaning
  the same package can exist at multiple versions within its build pool. For
  instance, if you depend on a specific version of a script for building a
  module.
- **restricted**: these dependencies (and their `deps.restricted`, etc) must
  have only a single version per `pkgName.name`. This is for languages who's
  `import` mechanics are dependent on having only a single version available.
  Examples: python, javascript, C
- **restrictedMajor** or **restrictedMinor**: like **restricted**, these
  dependencies (and their `deps.restrictedMajor`, etc) must have only a single
  version per _major/minor version_ of any `pkgName.name`.
  - For **major** you can have another version if it is a different major version
    (i.e both 3.2.1 and 2.2.1 can be used, but not 2.1.1 as well)
  - For **minor** you can have another version if it is a different major OR minor
    version (i.e. both 2.2.1 and 2.1.1 can be used, but not 2.2.3 as well)
- **global**: these are dependencies which _must_ be specified in the top-level
  package or one of it's _local_ dependencies (i.e. a local path to a file).
  This is typically used for things like compiler version, encryption library
  version, etc. Unlike other dependencies, these are specified as a function
  `function(depMap) -> list[depReq]`.
  - **depMap** must be a (possibly) nested object of global dependencies
    which follows some language convention, i.e. `lang.sh`, `lang.clang`,
    `lang.python.python2`, `system.lib.libc`, `system.lib.openssl`, etc
  - The `function(depMap)` must then convert the given global dependencies
    into the versions it wants for that package.
    - note: technically it can use a different version, although frequently
      items in **global** are also **locked**.


All **restricted** lists are _transitive_, meaning that if a dependency is
**restricted** and itself contains **restricted** dependencies, then they are
all part of the same "pool" which must have exactly matching dependencies. This
caries through _any_ restricted dependency, and if a dependency is in more than
one restricted pool then the most exclusive will take precedence.

The advantage of this is that **unrestricted** dependencies are allowed to have
their own dependency pool. So if you depend on the applications `PostgreSQL`
and `MongoDB` they do not have to have matching dependencies -- they can both
be listed as **unrestricted** dependencies and built within their own isolated
dependency "pools".

Similarily, if a library is being built stand-alone it can be listed as
**unrestricted**. An example might be if a python library uses a C library
internally. That C library's dependencies don't have to be shared within the
"python build system", the library's usage is contained to that single python
module.

## readPkg method
Input Params:
- **tmp**: temporary directory to store downloaded packages, typically gotten
  from the [Store].
- **remote**: see `resolvePkgs`
- **signatures**: see `resolvePkgs`
- **credentials**: see `resolvePkgs`

Outputs:
- **pkgPaths**: list of `pkgPath` objects, typically to be passed to the [Store].

The `readPkg` method downloads the packages returned by **resolvePkgs** into a
temporary directory.


# Store Override: Override where to store completed objects
# (SPC-store) <a id="SPC-store" />

`root.store` can be (optionally) set to an `exec` who's
`container=wake.LOCAL_CONTAINER` and `args`, `env` and `config` are all `null`
(must be fully self contained and cross-platform).

The [Store] exec is passed to every **container** and must be supported by
all containers. A good example would be a distributed filesystem which all
types of containers (and the user's computer) use to mount the required
fsentries for building modules.

This exec must support the following [JSH] API

## Tmp Methods
- **createTmp** method: get a readable empty directory to store data
  - outputs: string path to a temporary directory on the local filesystem.
- **deleteTmp** method: clear a tmp directory
  - params:
    - dir: the path to the directory

## Package Methods
- **readPackages** method: query the store for a list of packages
  - params:
    - versions: list of pkgVer strings.
  - outputs: `pkgPath` or `NotFound` objects.
- **createPackage** method: create an entry for the package at the specified
  directory. The directory may be moved or deleted by calling this method
  unless `keep` is `true`.
  - params:
    - dir (string): directory of downloaded package
    - pkgVer: the exact package version
    - keep: if `true` the directory must not be moved or deleted (default
      `false`).
  - outputs: `{"pkgPath": <pkgPath>}`


# Credentials Override (SPC-credentials) <a id="SPC-credentials /a>
This is how a user/group/company can create and share their own trusted
dependency credentials, using their group/company specific secret sharing
mechanism.

This is currently poorly defined, but the basic idea is:

- User defines hashed credentials in (or imported within)
  `$WAKEPATH/user.jsonnet`. This could also be re-generated every time `wake
  build` is run.
- **wakeCredentialsOverride** is called with these credentials and the
  container environment to generate LST.

Something like that... more design is necessary.


# Wake Cmdline Utility

The cmdline utility is what manages the build and execution phases, moving through
the following **phases**:
  - _packageLocal_: the root package's jsonnet is executed. All the [Store] and
    [Package Manager] are defined and all local packages are given to the
    [Store].
  - _packageRetrieve_: **wake cmdline** talks to the **packageManager** to
    determine and download all needed dependencies, which are given to the
    [Store].
  - _moduleBuild_: the root package's jsonnet is re-executed. `getPkg` will now
    return the _defined_ package object and `exports` can be called.

    [Store] creates a sandbox where each `package.exec` (with data)
    can be executed within its `container`. This creates a `module`, which can
    be a dependency of a later `package.exec`
  - _moduleExec_: modules can then be executed in a stateful fashion to (for
    example):
    - run tests
    - start services
    - act as traditional software

## Special Files and Directories

- [[.pkgFile]] `./PKG.libsonnet` file which contains the call to [[SPC-api.declarePkg]]
- [[.wakeDir]] `./.wake/`: reserved directory for containing wake metadata. Should
  not be used by users. Can contain the following fsentries:
  - `pkgs.libsonnet` file containing the imports to already defined pkgs. This
    is regenerated each cycle in the **phasePkgComplete** with the currently
    known pkgs.
  - `run.jsonnet` which is used for executing each cycle. Essentially each
    cycle is a call to `jsonnet .wake/run.jsonnet`, with the `pkgsLibFile`
    updated each time.
  - `fingerprint.json` file which is auto-generated by the build system for
    local pkgs, and required to match the cryptographic hash for retrieved pkgs
    or modules. This can also contain other non-hashable data like the
    signature of the fingerprint hash.
  - `localStore/` directory containing only _local_ pkg definitions. Used for
    pkg overrides.
  - `localDependencies.json` file containing a map of `path: pkgVer`. This is
    automatically generated when building local dependencies and is used to
    retrieve "locked" dependencies of external depdendencies.


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
    pkgName = req.pkgName()  # i.e. pkgB(>2.0) -> pkgB
    for available in pkgsAvailable[pkgName].reverse():
        if req.matches(available):
            return available
    return None
```

There is now one more step. We reduce all reqs down to groups by joining them
all together.

```python
def construct_req_muts():
    req_muts = {}  # Map[pkgName, set[req]]

    for pkgVer, reqs in pkgsReqs:
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
  - all `getPkg` calls are now full `pkgVer`.
  - all `getModule` calls are now `modVer`
  - all `file` objects are now paths to valid files or symlinks
  - the `exec` object will have all it's attributes expanded and files
    realized.
- `pkg-ready.json` and `module-ready.json`: the instantiated config manifest
  for a module/pkg. The same as `config.json` except the `file` objects are still `file` objects
  (but with pkgVers), since the paths have not been created in the build container.
- `pkgPaths.json`: a json file containing an object with key=pkgVer, value=path.
  Exists only in the container (when paths exist).
  This file exists when a module is inside its execution container and the paths
  resolve to their corresponding pkg.
- `modulePaths.json`: a json file containing an object with key=modVer, value=path.
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

# SPC-api
```
partof:
 - SPC-arch

subparts:
 - pkgVer
 - pkgReg
 - getPkg
 - declarePkg
 - declareModule
 - pathRef
 - exec
```

This details the API of `wake.jsonnet`. See links in the ".subarts" below to
the implementation and further documentation.

The basic API of wake is:
- Declare a PKG.jsonnet which is must return a `function(wake) -> wake.declarePkg(...)`, which itself returns
  a call to `wake.declarePkg(...)`
    - A pkg is _just data_ (files)
- The pkg then goes through multiple states as its dependencies are resolved.
  These states are _declared_ -> _defined_ -> [_ready_ ->] _completed_, where
  _ready_ is only for modules.
  - Closures on the pkg (like `exports`) are called when the pkg has achieved a
    state marked with the name of the input, i.e. `pkgDefined` is a pkg in
    state _defined_.
- Modules are of type `function(wake, pkgReady, config) ->
  wake.defineModule(...)` and return a call to `wake.defineModule`. Modules
  define what is built and how it is built.
  - Modules are hashed as the pkg (just data) the `config` passed to them, as
    well as any modules they depend on.

## Wake API

- [[.pkgVer]]: the uniq id (including exact version and hash) of a specific
  pkg. Used for pkg lookup.
- [[.pkgReq]]: defines a semver requirement for a `getPkg` call to retreive.
- [[.getPkg]]: retrieve a pkg lazily.
- [[.declarePkg]]: declare a pkg.
- [[.declareModule]]: declare how to build something with a pkg.
- [[.pathRef]]: Reference a path from within a pkg or module.
- [[.exec]]: a declared executable. Is typically a member of `module.exec`
  or can be a member of `exports` for a pkg or module.

[JSH]: http://github.com/vitiral/jsh
[semver]: https://semver.org
[Package Manager]: #SPC-packageManager
[Store]: #SPC-store
[Credentials Manager]: #SPC-credentials
