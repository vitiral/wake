//! Serialized types
use ergo::*;
use jsonnet::JsonVal;

#[derive(Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Hash {
    pub encoding: Encoding,
    pub value: String,
}

#[derive(Debug, Eq, PartialEq, Serialize, Deserialize)]
pub enum Encoding {
    AES256,
}

#[derive(Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ModuleId {
    pub hash: Hash,
    pub deterministic: bool,
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

#[derive(Debug, Eq, PartialEq, Serialize, Deserialize)]
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
                "encoding": "AES256",
                "value": "deadbeef"
            }
        }
    "#,
    )
    .unwrap();
    let expected = Input::File(File {
        path: "some/path.txt".to_string(),
        hash: Hash {
            encoding: Encoding::AES256,
            value: "deadbeef".to_string(),
        },
    });
    assert_eq!(expected, result);
}
