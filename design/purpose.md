# REQ-arch

buildnet is architected upon the following pillars:

- `jsonnet` is the configuration language. All behavior from a user's
  perspective can be imported through the `buildnet.libsonnet` entry point.
  All configurations are representable in JSON.
- `wasm` is the sandboxing and execution model. All wasm is executed in a
  sandbox.
- The core is written in `rust`, but could very easily be written in any
  language. The design simply requires hooks to be executed by (any) native
  language.
- It is easy to extend the build system using any language that can compile
  to `wasm`. Languges which can cross-compile their _compiler_ to `wasm` can
  use buildnet as both a package manager and a build system.


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
buildnet) configuration.

Returns: `value + {type: "config"}`

## `hash(encoding, value)` ([[.hash]])
A hash value of an encoding within `HASH_ENC_VARIANTS`.

## `moduleId(hash, deterministic)` ([[.moduleId]])

The moduleId is the internal representation of a module. It is
what the build system "sees" a module as.

`deterministic` specifies whether the moduleId can be used by other modules,
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

## `ref(moduleId, output)`([[.ref]])

A reference to an output from another module.

Args:
- `moduleId`: the module to reference.
- `output`: the output key to reference from the module.

Returns: `ref` object.

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

## `module(...)` ([[.module]])

Declare a module, which results in a `moduleId`.

This function can include files in the local directory. It will hash all of the
input arguments and return a `moduleId`, resolving any referenced modules first.

Arguments:
- `name`: the name to give to the module. This is only used as a hash and for
  publishing and user-reference.
- `version`: version to distinguish the module from others with the same name (it is
  acceptible to have multiple modules with different versions).
- `namespace=null`: a further disambiguity between modules with the same name
  and version.  Used by organiations to control where modules come from.
- `inputs=null`: A list of `file` or `ref` objects, which are included in the sandbox
  when the build is executing.
- `outputs=null`: A flat Object of outputs, which must be of type `path`,
  `file` or `config`.
- `exec=null`: The command and config to run to kick off the build. If null,
  the inputs and outputs must be files which already exist.
- `is_local=false`: If true, this module can only have inputs and outputs of
  type `file` (it must have no dependencies and generate no artifacts). It can
  then be executed by a `moduleExec`.

Returns: `moduleId`

## `moduleImport(...)` ([[.moduleImport]])

Import a module from a module factory.

This is the fundamental method for "importing" modules in the local filesystem.

The module at `path` must be a `.libsonnet` file of the following signature:

```jsonnet
function(env, config=null) {
    // -- implementation here --

    moduleId: functionThatResolvesToModuleId(...)
}
```

Arguments:
- `env`: the `env` object to use for building the module.
- `path`: The path to the module. Must be a local, relative path.
- `config`: `config` object that can be used to configure the module.

Returns: the resulting moduleId

## `moduleExec(...)` ([[.moduleEffect]])

Executes a **local** `module`, creating a new module.

The execution happens in an extended sandbox that has access to internet
sockets.

This method can be used to extend the build system to (for example) download
modules from the internet, or use other implementation-specific infrastructure
for caching and finding modules.

It is essential that implementors of `moduleEffect` are _entirely deterministic_
based on their inputs, and demonstrate _no side effects_. **Cached values will
be used when inputs are identical**.

Arguments:
- `name`: the name of the resulting module. Must match the module that is
  downloaded.
- `moduleId`: the local moduleId to use for execution.
- `exec`: the execution and config to use from within the local module.

Returns: the resulting `moduleId`.

## `sideEffect(...)` ([[.effect]])
Execute a side effect in an extended sandbox.

This can be included as an output in modules, but cannot be referenced
by other modules (as it is not deterministic). It can then be
used to spin up further (dependent) services or run tests.

It returns a `moduleId`, which behaves like a normal module the specified
`outputs`.

Arguments:
- `moduleId`: the moduleId to execute.
- `exec`: the execution and config to use from within that module.
- `outputs`: see [[REQ-api.module]].

Returns: `moduleId`.
