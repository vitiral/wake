# REQ-arch

wake is architected upon the following pillars:

- `jsonnet` is the configuration language. All behavior from a user's
  perspective can be imported through the `wake.libsonnet` entry point.
  All configurations are representable in JSON.
- `wasm` is the sandboxing and execution model. All wasm is executed in a
  sandbox.
- The core is written in `rust`, but could very easily be written in any
  language. The design simply requires hooks to be executed by (any) native
  language.
- It is easy to extend the build system using any language that can compile
  to `wasm`. Languges which can cross-compile their _compiler_ to `wasm` can
  use wake as both a package manager and a build system.


# REQ-user
partof: REQ-arch
###

> Because jsonnet does not have API documentation rendering builtin, this
> artifact will be used as the user documentation.

To use jsonnet, a user first writes a `.jsonnet` file, which looks something
like [`examples/hello.jsonnet ](../examples/hello.jsonnet)

The jsonnet file must export only a function, which takes an `env` parameter
as its first argument and a `config` object as its second.

Consult [[REQ-api]] for the full module exported into `env.std`.

# REQ-api
partof: REQ-arch
###

## `config(value)` ([[.config]])
An arbitrary untyped (or type=config) blob of json. Note that the `type`
keyword is reserved.

This is used in other functions to mean an arbitrary (from the perspective of
wake) configuration.

Returns: `value + {type: "config"}`

## `hash(encoding, value)` ([[.hash]])
A hash value of an encoding within `HASH_ENC_VARIANTS`.

## `modVer(pkg, hash, deterministic)` ([[.modVer]])

The modVer is the internal representation of a module. It is
what the build system "sees" a module as.

`deterministic` specifies whether the modVer can be used by other modules,
or whether it can only be used by `sideEffect` objects.

See [[REQ-api.module]] for more info.

## `path(components)` ([[.path]])
Properly joins the components into a valid path (string).

A valid path must be _both_ local and relative, meaning it:
- Must start with `./` or be the equivalent (start without a folder).
- Has no `..` remainiing after symantically resolving them.

This function will symantically resolve the path and verify it is valid.

Returns: `string`

## `file(path)` ([[.file]])
A local file which exists before the build step.

The hash will be calculated and included in the object.

Returns: `file`

## `oref(modVer, output)`([[.oref]])

A reference to an output from another module.

Args:
- `modVer`: the module to reference.
- `output`: the output key to reference from the module.

Returns: `oref` object.

## `pref(id, path)` ([[.pref]])

A reference to a path in a pkg or module.

Args:
- `id`: the pkgVer or modVer to reference.
- `path`: the path to the file to reference.

Returns: `pref` object.

## `ln(ref, path)` ([[.ln]])
A local link from either a `ref` or local path to a new local path.

Args:
- `ref`: the ref or path to use
- `path`: the _local_ path to place the link.

Returns: `file`

## `dir(include, exclude=null)` ([[.dir]])
Path to a directory of files to glob-include.

All matching sub files and directories will be recursively included,
except those listed in `exclude`.

Returns: `List[file]`

## `dump(config, path)` ([[.dump]])
Dumps the resolved config at the path as json. Can be used
as an input or output.

Arguments:
- `config`: arbitrary config object.
- `path`: the path to put the json.

Returns: `file`

## `load(path)` ([[.load]])
Load the path in the module as json into the build system.

Returns: `config`

## `exec(...)` ([[.exec]])

Execute a single `.wasm` file and accompaying config and args.

The `.wasm` file will be executed in a sandbox as part of a `module` with the
inputs unpackaged in its local directory.

- `file`: the `file` object to execute in the module.
- `config`: a `config` object, which will be passed through stdin to the exec.
- `args` extra arguments for the command. It is recommended to keep them
  extremely brief.

## `pkg(...)` ([[.pkg]])
Declare a pkg, which is the primary unit of _source_ organization in wake.

This must be declared in the `PKG` file in the base directory of the
source, which must look like this:

```
// PKG file
// -- user defined imports, etc --

function(env) {
    // -- any locals, etc --

    // must return the pkg in this way.
    return: env.std.pkg(...)
}
```

Arguments:
- `name`: the name to give to the package. This is only used as a hash and for
  publishing and user-reference.
- `version`: version to distinguish the module from others with the same name (it is
  acceptible to have multiple modules with different versions).
- `namespace=null`: a further disambiguity between modules with the same name
  and version.  Used by organiations to control where modules come from.
- `inputs=null`: A list of `file` or `ln` objects.

Any referenced `file` and `config` objects will define what items are included
in the pkg (which is just a blob of data), whereas `ln` objects will be used by
the `resolution` phase to resolve dependencies (and make sure all dependencies
are met). Recall that `ln` uses `pref` or `oref`, which fundamentally refers to
_other packages_.

The returned `pkg` is simply a flat manifest containing all the associated
metadata and local files. It can thus easily be packaged into a `.nar` file or
otherwise stored to be retrievable either localy or on a network.

Returns: `pkg`

## `module(...)` ([[.module]])

Declare a module, which results in a `modVer`.

Arguments:
- `name`: the module name.
- `pkg`: the pkg the module is based on. This determines the name, version, namespace,
  and inputs for the module.
- `orefs=null`: Additional references to outputs. Must be to modules defined
  in `pkg.infputs`.
- `outputs=null`: A flat Object of outputs, which must be of type `path`,
  `file` or `config`.
- `exec=null`: The command and config to run to kick off the build. If null,
  the inputs and outputs must be files which already exist.
- `is_local=false`: If true, this module can only have inputs and outputs of
  type `file` (it must have no dependencies and generate no artifacts). It can
  then be executed by a `execModule`.

Returns: `modVer`

## `moduleImport(...)` ([[.moduleImport]])

Import a module.

This is the fundamental method for "importing" modules in the local filesystem.

The module at `path` must be a `.libsonnet` file of the following signature:

```jsonnet
function(env, config=null) {
    // -- implementation here --

    return: functionThatResolvesToModuleId(...)
}
```

Arguments:
- `env`: the `env` object to use for building the module.
- `pkgVer`: the package to import the module from.
- `path`: The local path in the pkg to the module.
- `config`: `config` object that can be used to configure the module.

Returns: `modVer`

## `execModule(...)` ([[.execModule]])

Executes a **local** `module`, creating a `pkg`.

The execution happens in an extended sandbox that has access to internet
sockets.

This method can be used to extend the build system to (for example) download
packages from the internet, or use other implementation-specific infrastructure
for caching and finding packages.

It is essential that implementors of `execModule` are _entirely deterministic_
based on these inputs, and demonstrate _no side effects_. Notably, the build
system will use the hashed values on the inputs to create the `pkgVer` used to
store the package, which will be passed as part of the `config` as `execPkgId`.
The directory will be set as the `currentDir` when executing in the sandbox,
which is where the files can be stored.

Arguments:
- `name`: the name of the resulting module. Must match the module that is
  downloaded.
- `modVer`: the _local_ modVer to use for execution.
- `exec`: the execution and config to use from within the local module.

Returns: `pkg`

## `sideEffect(...)` ([[.effect]])
Execute a side effect in an extended sandbox.

This can be included as an output in modules, but cannot be referenced
by other modules (as it is not deterministic). It can then be
used to spin up further (dependent) services or run tests.

It returns a `modVer`, which behaves like a normal module the specified
`outputs`.

Arguments:
- `modVer`: the modVer to execute.
- `exec`: the execution and config to use from within that module.
- `outputs`: see [[REQ-api.module]].

Returns: `modVer`.

## SPC-arch
The high level architecture of wake is split into execution phases.

### `init` Phase
In `init`, wake loads `${WAKEENV}/env.jsonnet` to initialize `env`.
- Only `env.std` functions exists for loaded packages or modules and no
plugins are available.
- Several functions in `env.std` will return errors, including;
- `pkgVer`: package lookup is not allowed.
- `module(... is_local=false)`: can only instantiate local modules.
- `execModule`: no side effects are allowed in this phase.
- Any function which depends on the above. In general, packages in this phase
  must be self-contained sets of files.
- Any found `pkg` is put in `${WAKEIDS}/pkgs/{pkgVer}`

### `init-build` Phase
Any initialized _local_ `module` is hashed and put in
`${WAKEIDS/modules/{modVer}` (the entire build phase).

### `resolve-dependencies` Phase

After the `init` phases, the `env` has plugins (local modules which can be
executed with `execModule`). It then loads the local `PKG` in `modulePath` which
contains the full `env`.

In this phase, `execModule` calls can download new packages (or otherwise set
links which are equivalent of downloads).

### `build` Phase
The returned `json` blob contains instantiated `module` objects, but those
objects do not have any representation in a file system.

In this phase, the build system determines the ordering of modules that need
to be built, and executes it's build plugin to do so.

Note: `wake` does not determine _how_ builds are executed, it only executes
the associated plugin (`.wasm` file) to do so.


# SPC-arch2


