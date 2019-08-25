import os
from . import utils

DIR_WAKELIB = os.path.dirname(os.path.abspath(__file__))
DEFAULT_PKG_LIBSONNET = "PKG.libsonnet"
DEFAULT_DIGEST_JSON = ".digest.json"

_wakeConstants = utils.jsonloadf(
    os.path.join(DIR_WAKELIB, "wakeConstants.json"))

WAKE_SEP = _wakeConstants["WAKE_SEP"]

F_TYPE = _wakeConstants["F_TYPE"]
F_STATE = _wakeConstants["F_STATE"]
F_DIGEST = _wakeConstants["F_DIGEST"]
F_DIGESTTYPE = _wakeConstants["F_DIGESTTYPE"]

T_OBJECT = _wakeConstants["T_OBJECT"]
T_PKG = _wakeConstants["T_PKG"]
T_MODULE = _wakeConstants["T_MODULE"]
T_PATH_REF_PKG = _wakeConstants["T_PATH_REF_PKG"]

S_UNRESOLVED = _wakeConstants["S_UNRESOLVED"]
S_DECLARED = _wakeConstants["S_DECLARED"]
S_DEFINED = _wakeConstants["S_DEFINED"]
S_COMPLETED = _wakeConstants["S_COMPLETED"]

C_READ_PKGS = _wakeConstants["C_READ_PKGS"]
C_READ_PKGS_REQ = _wakeConstants["C_READ_PKGS_REQ"]

DIR_WAKE = _wakeConstants["DIR_WAKE"]
FILE_WAKELIB = _wakeConstants["FILE_WAKELIB"]  #wake.libsonnet
FILE_PKG_DEFAULT = _wakeConstants["FILE_PKG_DEFAULT"]  # PKG.libsonnet
FILE_PKGS = _wakeConstants["FILE_PKGS"]
FILE_RUN_DIGEST = "wakeRunDigest.jsonnet"

# Commong paths and data
PATH_WAKELIB = os.path.join(DIR_WAKELIB, FILE_WAKELIB)
RUN_EXPORTS_TEMPLATE = utils.loadf(
    os.path.join(DIR_WAKELIB, "wakeRunExports.jsonnet"))
RUN_DIGEST_TEMPLATE = utils.loadf(os.path.join(DIR_WAKELIB, FILE_RUN_DIGEST))
