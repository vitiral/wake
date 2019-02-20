//! Serialized types
use ergo::*;

#[derive(Clone, Debug, Eq, Hash, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct PkgInfo {
    name: String,
    namespace: String,
    version: String,
}

#[derive(Debug, Eq, Hash, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Hash {
    pub value: String,
}

impl From<&str> for Hash {
    fn from(s: &str) -> Self {
        Hash {
            value: s.to_string(),
        }
    }
}

impl From<String> for Hash {
    fn from(s: String) -> Self {
        Hash { value: s }
    }
}

#[derive(Debug, Eq, PartialEq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ModuleId {
    pub hash: Hash,
    pub deterministic: bool,
}

impl ModuleId {
    pub fn new(hash: Hash) -> Self {
        Self {
            hash: hash,
            deterministic: true,
        }
    }
}

impl From<&str> for ModuleId {
    fn from(s: &str) -> Self {
        Self::new(s.into())
    }
}

#[derive(Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct File {
    pub path: String,
    pub hash: Hash,
}

#[derive(Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Ref {
    pub module_id: ModuleId,
    pub output: String,
}

#[derive(Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Exec {
    pub file: File,
    pub config: File,
    pub args: Vec<String>,
}

#[derive(Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(tag = "type", rename_all = "camelCase")]
pub enum Input {
    File(File),
    Ref(Ref),
    Exec(Exec),
    ModuleId(ModuleId),
}

#[derive(Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(tag = "type", rename_all = "camelCase")]
pub enum Output {
    File(File),
    Path(String),
    Exec(Exec),
}

#[derive(Debug, Default, Eq, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Module {
    pub name: String,
    pub version: String,
    pub namespace: Option<String>,
    pub inputs: Vec<Input>,
    pub outputs: Vec<Output>,
}

#[test]
fn test_input_ser() {
    let result: Input = json::from_str(
        r#"
        {
            "type": "file",
            "path": "some/path.txt",
            "hash": {
                "value": "deadbeef"
            }
        }
    "#,
    )
    .unwrap();
    let expected = Input::File(File {
        path: "some/path.txt".to_string(),
        hash: Hash {
            value: "deadbeef".to_string(),
        },
    });
    assert_eq!(expected, result);
}
