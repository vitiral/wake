- The [Package Manager] which is a cmdline utility which is called by the **wake
  cmdline**. It's job is to solve the dependency graph and retrieve packages
  from the internet (or elsewhere).


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
- **remote**: map of `pkgVer: pkgsRemote` specifying how to retrieve the
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

To help determine this isolation, **deps** allows for specifying several
levels of restrictions on dependencies (see **deps**).

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


