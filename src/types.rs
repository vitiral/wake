//! Serialized types
use ergo::*;
use jsonnet::JsonVal;

#[derive(Debug, Eq, PartialEq, Serialize, Deserialize)]
pub struct Hash {
    pub encoding: Encoding,
    pub value: String,
}

#[derive(Debug, Eq, PartialEq, Serialize, Deserialize)]
pub enum Encoding {
    AES256,
}

#[derive(Debug, Eq, PartialEq, Serialize, Deserialize)]
pub struct ModuleId {
    pub hash: Hash,
    pub deterministic: bool,
}

#[derive(Debug, Eq, PartialEq, Serialize, Deserialize)]
pub struct File {
    pub path: String,
    pub hash: Hash,
}

#[derive(Debug, Eq, PartialEq, Serialize, Deserialize)]
pub struct Ref {
    pub module_id: ModuleId,
    pub output: String,
}

#[derive(Debug, Eq, PartialEq, Serialize, Deserialize)]
pub struct Exec {
    pub file: File,
    pub config: File,
    pub args: Vec<String>,
}

#[derive(Debug, Eq, PartialEq, Serialize, Deserialize)]
pub enum Input {
    File(File),
    Ref(Ref),
    Exec(Exec),
    ModuleId(ModuleId),
}

#[derive(Debug, Eq, PartialEq, Serialize, Deserialize)]
pub enum Output {
    File(File),
    Path(String),
    Exec(Exec),
}

#[derive(Debug, Eq, PartialEq, Serialize, Deserialize)]
pub struct Module {
    pub name: String,
    pub version: String,
    pub namespace: Option<String>,
    pub inputs: Vec<Input>,
    pub outputs: Vec<Output>,
}
