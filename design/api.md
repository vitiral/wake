# SPC-api
partof: REQ-purpose
###

Below are the different types/functions that make up the core API of wake.

Some special notes:

- files can only be defined in `files`. Any reference to a "file" in inputs or outputs
  (or anywhere) will simply be its raw data (json, string, etc).

## [[.pkgInfo]] `pkgInfo(...)`
This is the information that defines a package. It results in an object which
is used as part of other types.

Arguments:
- `name`: the name to give to the pkg.
- `version`: semantic version used when resolving packages.
- `namespace=null`: a disambiguity between modules with the same name and
  version.  Used by organiations to control where modules come from.


## [[.pkg]] `pkg(...)`
Defines a pkg. Must be the only thing returned from the `./PKG` file.

Arguments:
- `pkgInfo`
- `files=list[path]`: a list of paths to _local_ files to include. This automatically
  includes `PKG` itself and paths in `modules`, and is used to compute the hash of
  the PKG.
  `inputs=function(wake, pkg) -> map`: function which takes in the instantiated `pkg`
  and returns a flat map of key/values. The values are _strongly typed_ and can
  include: ref, file.
- `pkgs`: flat map of key/pkgInfo. This is resolved first, and is used for
  finding and downloading pkgs.
- `modules=map[key, module]`: map of local modules of the pkg.
  `function(wake, pkg, config) -> moduleId`

> Note: the function defined in `inputs` is called at the beginning of this
> pkg's instantiation, only after all the `pkgs` this pkg is dependent on have
> been instantiated.


## [[.getPkg]] `getPkg(...)`
Retrieve a pkg.

Pkgs are _just data_ that can depend on other pkgs or the direct execution
of other pkgs (cannot depend on modules).

Arguments:
- `pkgInfo`
- `from`: one of:
  - ./path`: a reflike local path
  - `wake.GLOBAL` to retrieve from a globally defined pkg
  - `wake.exec(ePkg, ...)`: to execute another pkg to retrieve the pkg
- `global=null`: used to insert the pkg in the global namespace
  (`from=wake.GLOBAL`). Set to `true` to do so, `{override=[1..100]}` to
  set the override value.
- `permisions=null`: permissions to grant the pkg. `defineGlobal` is required
  for the retrieved pkg to _itself_ define global pkgs.

Returns: pkgInfo


## [[.module]] `module(...)`

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


## [[.getModule]] `getModule(...)`
Retrieve a module from a pkg with a specified config.

Arguments:
- `pkg`
- `
- `from`: one of:
  - ./path`: a reflike local path
  - `wake.GLOBAL` to retrieve from a globally defined pkg
  - `wake.exec(ePkg, ...)`: to execute another pkg to retrieve the pkg
- `global=null`: used to insert the pkg in the global namespace
  (`from=wake.GLOBAL`). Set to `true` to do so, `{override=[1..100]}` to
  set the override value.
- `permisions=null`: permissions to grant the pkg. `defineGlobal` is required
  for the retrieved pkg to _itself_ define global pkgs.

Returns: pkgInfo


## [[.exec]] `exec(...)`
Specification for executing from within a pkg.

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

Exec will be executed from within a sandbox where all dependent pkgs
and modules (and files which use them) will be properly linked. It
will be passed the `args` as arguments, and the config below in stdin.
The environment will be what was passed to `env` with the following additions:
- `PWD` is set to `config.base`


The following `config` will be passed as a json object to stdin of exec:
```
{
    "base": <the directory of the module>,
    "pkg": <the instantiated pkg manifest>,
    "module": <the instantiated module manifest>,
    "config": <the config manifest given to exec>,
    "env": <the env given to exec>,
}
```

## [[.file]] `file(path, from=ref, dump=false)`
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

# SPC-helpers
These are helper functions are not part of the core types.

##  [[.dir]]: `dir(include, exclude=null)`
Path to a directory of files to glob-include.

All matching sub files and directories will be recursively included,
except those listed in `exclude`.

Returns: `List[path]`


