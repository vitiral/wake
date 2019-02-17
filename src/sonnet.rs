//! Helper functions for working with jsonnet.

use ergo::*;
use jsonnet::*;
use std::ffi::OsStr;
use crate::types::{PkgInfo};
use expect_macro::expect;


lazy_static! {
    static ref pkgs_path: PathBuf = PathBuf::from("./.wake/pkgs");
    static ref PKGS: Mutex<IndexMap<PkgInfo, PathBuf>> = Mutex::new(IndexMap::new());
    static ref PKG_DECLARES: Mutex<IndexMap<PkgInfo, PkgDeclare>> = Mutex::new(IndexMap::new());
}

#[derive(Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(tag = "type", rename_all = "camelCase")]
enum NativeCalls {
    PkgDeclare(PkgDeclare),
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

fn wake_pkg_resolver<'a>(vm: &'a JsonnetVm, args: &[JsonVal<'a>]) -> Result<JsonValue<'a>, String> {
    let arg = args[0].as_str().ok_or("expected string config")?;
    let config: NativeCalls = json::from_str(arg).map_err(|e| e.to_string())?;

    let mut lock = expect!(PKG_DECLARES.lock());
    let declares = lock.deref_mut();

    match config {
        NativeCalls::PkgDeclare(pkg) => {
            if !declares.contains_key(&pkg.pkg_info) {
                declares.insert(pkg.pkg_info.clone(), pkg);
            }

        },
    }

    Ok(JsonValue::from_num(vm, 1.0))
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
    fn myimport<'a>(_vm: &'a JsonnetVm, base: &Path, rel: &Path) -> Result<(PathBuf, String), String> {
        if let Ok(id_path) = rel.strip_prefix(Path::new(id_path_prefix)) {
            let mut components = id_path.components();
            let id_str = components.next()
                .ok_or("id path had no id component.".to_string())?
                .as_os_str()
                .to_str()
                .ok_or("id component is not utf8".to_string())?;

            let index = id_str.rfind('-')
                .ok_or("id component does not have name".to_string())?;
            let (id, name) = id_str.split_at(index);
            let module_id = ModuleId::from(id);
            if !contains_module(&module_id) {
                return Err(format!("Module does not exist: {}", id_str));
            }

            // TODO: improve this
            Ok((base.into(), "2 + 3".to_owned()))
        } else if rel.has_root() {
            Err(format!("All non-id paths must be relative: {}", rel.display()))
        } else {
            // TODO: resolve the local path
            Err(format!("not found in base={}, rel={}", base.display(), rel.display()))
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
