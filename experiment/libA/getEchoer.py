#!/usr/bin/python3

# A pkg retriever which simply creates a pkg with a single
# export, "echoer". Echoer accepts an optional path and echos
# its version either to a file at that path or stdout.
#
# This is used only for testing and validation purposes.

import sys
import os
import json

def dumpf(p, txt):
    with open(p, 'w') as f:
        return f.write(txt)

def jsonloadf(p):
    with open(p) as f:
        return json.load(f)


DIR_WAKE = ".wake"
C = jsonloadf(os.path.join(DIR_WAKE, "wakeConstants.json"))

F_TYPE = C['F_TYPE']
C_READ_PKGS = C['C_READ_PKGS']
C_READ_PKGS_REQ = C['C_READ_PKGS_REQ']
WAKE_SEP = C['WAKE_SEP']
DIR_RETRIEVED = C["DIR_RETRIEVED"]
FILE_PKG = C["FILE_PKG"]

PKG_TEMPLATE = '''
function(wake)
    local echoPath = "./echo";

    wake.declarePkg(
        fingerprint=import ".wake/fingerprint.json",
        namespace="{namespace}",
        name="{name}",
        version="{version}",
        paths=[echoPath],
        exports = function(wake, pkg) {{
            "echoBin": wake.pathRef(pkg, echoPath),
        }},
    )
'''

ECHO_TEMPLATE = '''
#!/bin/bash
echo "{version}"
'''

class Pkg(object):
    def __init__(self, namespace, name, version):
        vlist = [int(v) for v in version.split('.')]
        assert len(vlist) == 3

        self.namespace = namespace
        self.name = name
        self.version = version

    @classmethod
    def from_str(cls, pkgReq):
        sp, name, vreq = pkgReq.split(WAKE_SEP)
        return cls(sp, name, vreq)

    def __repr__(self):
        return WAKE_SEP.join((self.namespace, self.name, self.version))


cmd = json.load(sys.stdin)
cmdt = cmd[F_TYPE]

if cmdt == C_READ_PKGS_REQ:
    out = {}

    for pkgReq in cmd['pkgReqs']:
        pkgReq = Pkg.from_str(pkgReq)
        # version always == pkgReq
        version = str(pkgReq)
        out[version] = {'version': version, 'pkgs': []}

    json.dump(out, sys.stdout)
    sys.stdout.write('\n')
    sys.exit(0)

elif cmdt == C_READ_PKGS:
    retrievedDir = os.path.join(DIR_WAKE, DIR_RETRIEVED)
    os.mkdir(retrievedDir)

    for pkg in cmd['pkgVersions']:
        pkg = Pkg.from_str(pkg)

        pkgPath = os.path.join(retrievedDir, str(pkg))
        os.mkdir(pkgPath)

        # create the bash "echo" file
        echoBash = ECHO_TEMPLATE.format(version=pkg.version)
        echoBashPath = os.path.join(pkgPath, 'echo')
        dumpf(echoBashPath, echoBash)
        os.chmod(echoBashPath, 0o755)

        # create the PKG.libsonnet file
        pkgDeclare = PKG_TEMPLATE.format(
            namespace=pkg.namespace,
            name=pkg.name,
            version=pkg.version,
        )
        dumpf(os.path.join(pkgPath, FILE_PKG), pkgDeclare)

    sys.exit(0)

raise ValueError("unknown command: " + cmdt)
