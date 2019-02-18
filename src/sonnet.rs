//! Helper functions for working with jsonnet.

use crate::types::PkgInfo;
use ergo::*;
use expect_macro::expect;
use jsonnet::*;
use std::ffi::OsStr;

lazy_static! {
    static ref pkgs_path: PathBuf = PathBuf::from("./.wake/pkgs");
    static ref GLOBALS: Mutex<Globals> = Mutex::new(Globals::default());
}

#[derive(Debug, Default)]
struct Globals {
    pub pkgs: IndexMap<PkgInfo, String>,
    pub pkg_declares: IndexMap<PkgInfo, PkgDeclare>,
    pub pkg_gets: IndexMap<PkgInfo, PkgGet>,
    pub pkg_globals: IndexMap<PkgInfo, String>,
}

#[derive(Debug, PartialEq, Serialize, Deserialize)]
#[serde(tag = "type", rename_all = "camelCase")]
enum NativeCalls {
    PkgDeclare(PkgDeclare),
    PkgGet(PkgGet),
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
struct PkgDeclare {
    pkg_info: PkgInfo,
    files: Vec<String>,
    inputs: IndexMap<String, String>,

    // TODO: these are not String
    pkgs: IndexMap<String, String>,
    modules: IndexMap<String, String>,
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
struct PkgGet {
    pkg_info: PkgInfo,
    from: PkgFrom,
    path: String,
    global: Option<PkgGlobal>,
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
#[serde(untagged)]
enum PkgFrom {
    Path(String),
    PkgGlobal,
    PkgExec(PkgExec),
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
struct PkgGlobal {
    #[serde(rename = "override")]
    override_: u16,
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
struct PkgExec {
    pkg: PkgInfo,
    exec: Exec,
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
struct Exec {
    path: String,
    config: json::Value,
    args: Vec<String>,
    env: json::Value,
}

pub fn wake_pkg_resolver<'a>(
    vm: &'a JsonnetVm,
    args: &[JsonVal<'a>],
) -> Result<JsonValue<'a>, String> {
    let arg = args[0].as_str().ok_or("expected string config")?;
    let config: NativeCalls = json::from_str(arg).map_err(|e| e.to_string())?;

    let mut lock = expect!(GLOBALS.lock());
    let globals = lock.deref_mut();

    let pkgs = &mut globals.pkgs;
    let pkg_globals = &mut globals.pkg_globals;
    let declares = &mut globals.pkg_declares;

    match config {
        NativeCalls::PkgDeclare(pkg) => {
            let info = &pkg.pkg_info;
            if let Some(path) = pkgs.get(info) {
                assert!(!declares.contains_key(info));
                Ok(JsonValue::from_str(vm, &path))
            } else {
                if !declares.contains_key(&pkg.pkg_info) {
                    declares.insert(pkg.pkg_info.clone(), pkg);
                }
                Ok(JsonValue::null(vm))
            }
        }

        NativeCalls::PkgGet(pkgGet) => {
            let info = &pkgGet.pkg_info;

            match pkgGet.from {
                PkgFrom::Path(path) => {
                    // FIXME: need to call the plugin here
                    Ok(JsonValue::null(vm))
                },

                PkgFrom::PkgGlobal => {
                    if let Some(path) = pkg_globals.get(info) {
                        // TODO: make sure nobody has tried to get the same pkg with
                        // a different exec
                        Ok(JsonValue::from_str(vm, &path))
                    } else {
                        Ok(JsonValue::null(vm))
                    }
                },

                PkgFrom::PkgExec( PkgExec { pkg, exec} ) => {
                    // TODO: make sure nobody has tried to get the same pkg with
                    // a different exec
                    if let Some(path) = pkgs.get(info) {
                        // TODO: make sure nobody has tried to get the same pkg with
                        // a different exec
                        Ok(JsonValue::from_str(vm, &path))
                    } else {
                        // FIXME: need to call the plugin here
                        Ok(JsonValue::null(vm))
                    }
                }
            }
        }
    }
}

#[cfg(test)]
mod test_old {
    use super::*;

    lazy_static! {
        static ref MODULES: Mutex<IndexMap<ModuleId, Module>> = Mutex::new(IndexMap::new());
    }

    fn insert_module(module_id: ModuleId, module: Module) {
        let mut lock = expect!(MODULES.lock());
        lock.deref_mut().insert(module_id, module);
    }

    fn contains_module(module_id: &ModuleId) -> bool {
        let lock = expect!(MODULES.lock());
        lock.deref().contains_key(module_id)
    }

    fn clear_modules() {
        let mut lock = expect!(MODULES.lock());
        lock.deref_mut().clear();
    }

    /// Best docs for this: https://github.com/google/jsonnet/issues/502
    fn myimport<'a>(
        _vm: &'a JsonnetVm,
        base: &Path,
        rel: &Path,
    ) -> Result<(PathBuf, String), String> {
        if let Ok(id_path) = rel.strip_prefix(Path::new(id_path_prefix)) {
            let mut components = id_path.components();
            let id_str = components
                .next()
                .ok_or("id path had no id component.".to_string())?
                .as_os_str()
                .to_str()
                .ok_or("id component is not utf8".to_string())?;

            let index = id_str
                .rfind('-')
                .ok_or("id component does not have name".to_string())?;
            let (id, name) = id_str.split_at(index);
            let module_id = ModuleId::from(id);
            if !contains_module(&module_id) {
                return Err(format!("Module does not exist: {}", id_str));
            }

            // TODO: improve this
            Ok((base.into(), "2 + 3".to_owned()))
        } else if rel.has_root() {
            Err(format!(
                "All non-id paths must be relative: {}",
                rel.display()
            ))
        } else {
            // TODO: resolve the local path
            Err(format!(
                "not found in base={}, rel={}",
                base.display(),
                rel.display()
            ))
        }
    }

    fn myadd<'a>(vm: &'a JsonnetVm, args: &[JsonVal<'a>]) -> Result<JsonValue<'a>, String> {
        let a = args[0].as_num().ok_or("Expected a number")?;
        let b = args[1].as_num().ok_or("Expected a number")?;
        Ok(JsonValue::from_num(vm, a + b))
    }

    #[test]
    fn test_import() {
        clear_modules();
        insert_module(ModuleId::from("abcde"), Module::default());
        let mut vm = JsonnetVm::new();
        vm.import_callback(myimport);
        {
            let output = vm
                .evaluate_snippet("myimport", "import '/wake/ids/abcde-name/bar.jsonnet'")
                .unwrap();
            assert_eq!(output.to_string(), "5\n");
        }

        // {
        //     let result = vm.evaluate_snippet("myimport", "import 'x/foo.jsonnet'");
        //     assert!(result.is_err());
        // }
    }

    #[test]
    fn test_native() {
        let mut vm = JsonnetVm::new();
        vm.native_callback("myadd", myadd, &["a", "b"]);

        {
            let result = vm.evaluate_snippet("nativetest", "std.native('myadd')(2, 3)");
            assert_eq!(result.unwrap().as_str(), "5\n");
        }

        {
            let result = vm.evaluate_snippet("nativefail", "std.native('myadd')('foo', 'bar')");
            assert!(result.is_err());
        }
    }

    pub fn exec() -> Result<String, String> {
        Ok("A-ok pops!".to_string())
    }
}
