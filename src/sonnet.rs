//! Helper functions for working with jsonnet.

use ergo::*;
use jsonnet::*;
use std::ffi::OsStr;

fn myimport<'a>(_vm: &'a JsonnetVm, base: &Path, rel: &Path) -> Result<(PathBuf, String), String> {
    if rel.file_stem() == Some(OsStr::new("bar")) {
        let newbase = base.into();
        let contents = "2 + 3".to_owned();
        Ok((newbase, contents))
    } else {
        Err("not found".to_owned())
    }
}

fn myadd<'a>(vm: &'a JsonnetVm, args: &[JsonVal<'a>]) -> Result<JsonValue<'a>, String> {
    let a = args[0].as_num().ok_or("Expected a number")?;
    let b = args[1].as_num().ok_or("Expected a number")?;
    Ok(JsonValue::from_num(vm, a + b))
}

#[test]
fn test_import() {
    let mut vm = JsonnetVm::new();
    vm.import_callback(myimport);
    {
        let output = vm
            .evaluate_snippet("myimport", "import 'x/bar.jsonnet'")
            .unwrap();
        assert_eq!(output.to_string(), "5\n");
    }

    {
        let result = vm.evaluate_snippet("myimport", "import 'x/foo.jsonnet'");
        assert!(result.is_err());
    }
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
