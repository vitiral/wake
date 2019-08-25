DIR_WAKELIB = path.dirname(abspath(__file__))
DEFAULT_PKG_LIBSONNET = "PKG.libsonnet"

wakelib = pjoin(HERE_DIR, "wake.libsonnet")
FILE_CONSTANTS = "wakeConstants.json"
wakeConstantsPath = pjoin(HERE_DIR, FILE_CONSTANTS)
wakeConstants = jsonloadf(wakeConstantsPath)

WAKE_SEP = wakeConstants["WAKE_SEP"]

F_TYPE = wakeConstants["F_TYPE"]
F_STATE = wakeConstants["F_STATE"]
F_DIGEST = wakeConstants["F_DIGEST"]
F_DIGESTTYPE = wakeConstants["F_DIGESTTYPE"]

T_OBJECT = wakeConstants["T_OBJECT"]
T_PKG = wakeConstants["T_PKG"]
T_MODULE = wakeConstants["T_MODULE"]
T_PATH_REF_PKG = wakeConstants["T_PATH_REF_PKG"]

S_UNRESOLVED = wakeConstants["S_UNRESOLVED"]
S_DECLARED = wakeConstants["S_DECLARED"]
S_DEFINED = wakeConstants["S_DEFINED"]
S_COMPLETED = wakeConstants["S_COMPLETED"]

C_READ_PKGS = wakeConstants["C_READ_PKGS"]
C_READ_PKGS_REQ = wakeConstants["C_READ_PKGS_REQ"]

## COMMON PATHS

FILE_PKG = wakeConstants["FILE_PKG"]  # #SPC-arch.pkgFile

# See #SPC-arch.wakeDir
DIR_WAKE = wakeConstants["DIR_WAKE"]
DIR_WAKE_REL = path.join(".", DIR_WAKE)
DIR_LOCAL_STORE = wakeConstants["DIR_LOCAL_STORE"]
DIR_RETRIEVED = wakeConstants["DIR_RETRIEVED"]

FILE_RUN = wakeConstants["FILE_RUN"]
FILE_PKG = wakeConstants["FILE_PKG"]
FILE_PKGS = wakeConstants["FILE_PKGS"]
FILE_STORE_META = "storeMeta.json"

FILE_FINGERPRINT = wakeConstants["FILE_FINGERPRINT"]
FILE_LOCAL_DEPENDENCIES = wakeConstants["FILE_LOCAL_DEPENDENCIES"]

## FILE WRITERS

_RUN_TEMPLATE = """
local wakelib = import "{wakelib}";
# local pkgsDefined = import "{pkgs_defined}";

local wake =
    wakelib
    + {{
        _private+: {{
            # pkgsDefined: pkgsDefined,
        }},
    }};

// instantiate and return the root pkg
local pkg_fn = (import "{pkg_root}");
local pkgInitial = pkg_fn(wake);

local root = wake._private.recurseDefinePkg(wake, pkgInitial);

{{
    root: wake._private.simplify(root),
    all: wake._private.recurseSimplify(root),
}}
"""


def format_run_template(wake_libsonnet, pkg_root):
    """Returned the wake jsonnet run template with items filled out."""
    return RUN_TEMPLATE.format(
        wakelib=wake_libsonnet,
        pkg_root=pkg_root,
        pkgs_defined="TODO",
    )
