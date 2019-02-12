# REQ-api
<details>
<summary><b>metadata</b></summary>
<b>partof:</b><br>
<li><a style="font-weight: bold; color: #FF4136" title="REQ-ARCH" href="#REQ-ARCH">REQ-arch</a></li>
<b>parts:</b> <i>none</i></a><br>
<b>file:</b> design/purpose.md<br>
<b>impl:</b> <i>not implemented</i><br>
<b>spc:</b>0.00&nbsp;&nbsp;<b>tst:</b>0.00<br>
<hr>
</details>


## `config(value)` (<span title="Not Implemented" style="color: #FF4136"><b><i>.config</i></b></span>)
An arbitrary untyped (or type=config) blob of json. Note that the `type`
keyword is reserved.

This is used in other functions to mean an arbitrary (from the perspective of
buildnet) configuration.

Returns: value + {type: "config"}

## `hash(encoding, value)` (<span title="Not Implemented" style="color: #FF4136"><b><i>.hash</i></b></span>)
A hash value of an encoding within HASH_ENC_VARIANTS`.

## `moduleId(hash, is_local)` (<span title="Not Implemented" style="color: #FF4136"><b><i>.moduleId</i></b></span>)
The moduleId is the internal representation of a module. It is
what the build system "sees" a module as.

See <a style="font-weight: bold; color: #FF4136" title="REQ-API.MODULE" href="#REQ-API">REQ-api.module</a> for more info.

## `path(components)` (<span title="Not Implemented" style="color: #FF4136"><b><i>.path</i></b></span>)
Properly joins the components into a valid path (string).

## `file(path)` (<span title="Not Implemented" style="color: #FF4136"><b><i>.file</i></b></span>)
A local file.

The hash will be calculated and included in the object.

## `rfile(path)` (<span title="Not Implemented" style="color: #FF4136"><b><i>.rfile</i></b></span>)
A result file. Only a path, with the hash computed later.

## `dir(include, exclude=null)` (<span title="Not Implemented" style="color: #FF4136"><b><i>.dir</i></b></span>)
Path to a directory of files to glob-include.

All matching sub files and directories will be recursively included,
except those listed in `exclude`.

returns: list[file]

## `dump(path, manifest)` (<span title="Not Implemented" style="color: #FF4136"><b><i>.dump</i></b></span>)
Dumps the resolved manifest at the path as json. Can be used
as an input or output.

Returns: `file`

## `load(path)` (<span title="Not Implemented" style="color: #FF4136"><b><i>.load</i></b></span>)
Load the path in the module as json into the build system.

Returns: an arbitrary Object.

## `ref(moduleId, output, path)`(<span title="Not Implemented" style="color: #FF4136"><b><i>.ref</i></b></span>)

A reference to an output from another module.

  In the build phase the reference will be resolved as files at specific paths.

Args:
- `moduleId`: the module to reference.
- `output`: the output object to reference.
- `path`: the path to put the output object.

## `exec(...)` (<span title="Not Implemented" style="color: #FF4136"><b><i>.exec</i></b></span>)

A single `.wasm` file and accompaying config and args.

The `.wasm` file will be executed in a sandbox as part of a `module` with the
inputs unpackaged in its local directory.

- `file`: the `file` object to execute in the module.
- `config`: a `config` object, which will be passed through stdin to the exec.
- `args` extra arguments for the command. It is recommended to keep them
  extremely brief.

## `module(...)` (<span title="Not Implemented" style="color: #FF4136"><b><i>.module</i></b></span>)

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
- `outputs=null`: A flat Object of outputs, which must be of type `rfile`,
  `file` or `config`.
- `exec=null`: The command and config to run to kick off the build. If null,
  the inputs and outputs must be files which already exist.
- `is_local=false`: If true, this module can only have inputs and outputs of
  type `file` (it must have no dependencies and generate no artifacts). It can
  then be executed by a `moduleExec`.

Returns: `moduleId`

## `modulePath(...)` (<span title="Not Implemented" style="color: #FF4136"><b><i>.modulePath</i></b></span>)

Refer to a module factory by path.

This is the fundamental method for "importing" modules in the local filesystem.

The module at `path` must be a `.libsonnet` file of the following signature:

```jsonnet
function(env, config=null) {
    // -- implementation here --

    moduleId: functionThatResolvesToModuleId(...)
}
```

Arguments:
- `path`: The path to another module. Must be a local, relative path.
- `config`: `config` object that can be used to configure the build.

Returns: the resulting moduleId

## `moduleExec(...)` (<span title="Not Implemented" style="color: #FF4136"><b><i>.moduleEffect</i></b></span>)

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

## `sideEffect(...)` (<span title="Not Implemented" style="color: #FF4136"><b><i>.effect</i></b></span>)
Execute a side effect in an extended sandbox.

This can be included as an output in modules, but cannot be referenced
by other modules (as it is not deterministic). It can then be
used to spin up services or run tests.

It returns a `moduleId`, which contains the specified `outputs`.

Arguments:
- `moduleId`: the moduleId to execute.
- `exec`: the execution and config to use from within that module.
- `outputs`: see <a style="font-weight: bold; color: #FF4136" title="REQ-API.MODULE" href="#REQ-API">REQ-api.module</a>.

Returns: `moduleId`.


# REQ-arch
<details>
<summary><b>metadata</b></summary>
<b>partof:</b> <i>none</i></a><br>
<b>parts:</b><br>
<li><a style="font-weight: bold; color: #FF4136" title="REQ-API" href="#REQ-API">REQ-api</a></li>
<li><a style="font-weight: bold; color: #FF4136" title="REQ-USER" href="#REQ-USER">REQ-user</a></li>
<b>file:</b> design/purpose.md<br>
<b>impl:</b> <i>not implemented</i><br>
<b>spc:</b>0.00&nbsp;&nbsp;<b>tst:</b>0.00<br>
<hr>
</details>


buildnet is architected upon the following pillars:

- `jsonnet` is the configuration language. All behavior from a user's
  perspective can be imported through the `buildnet.libsonnet` entry point.
  All configurations are representable in JSON.
- `wasm` is the sandboxing and execution model. All wasm is executed in a
  sandbox using `wasmer`.
- The core is written in `rust`, but could easily be written in any language.
- It is easy to extend the build system using any language that can compile
  to `wasm`. Languges which can cross-compile their _compiler_ to `wasm` can
  use buildnet as both a package manager and a build system.


# REQ-user
<details>
<summary><b>metadata</b></summary>
<b>partof:</b><br>
<li><a style="font-weight: bold; color: #FF4136" title="REQ-ARCH" href="#REQ-ARCH">REQ-arch</a></li>
<b>parts:</b> <i>none</i></a><br>
<b>file:</b> design/purpose.md<br>
<b>impl:</b> <i>not implemented</i><br>
<b>spc:</b>0.00&nbsp;&nbsp;<b>tst:</b>0.00<br>
<hr>
</details>


> Because jsonnet does not have API documentation rendering builtin, this
> artifact will be used as the user documentation.

To use jsonnet, a user first writes a `.jsonnet` file, which looks something
like `examples/hello.jsonnet  in this library.

The jsonnet file must export only a function, which takes an `env` parameter
as its first argument and an arbitrary `config` object as its second.

Consult <a style="font-weight: bold; color: #FF4136" title="REQ-API" href="#REQ-API">REQ-api</a> for the full module exported into `env.std`.


