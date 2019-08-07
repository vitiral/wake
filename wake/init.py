# ⏾🌊🛠 wake software's true potential
#
# Copyright (C) 2019 Rett Berg <github.com/vitiral>
#
# The source code is Licensed under either of
#
# * Apache License, Version 2.0, ([LICENSE-APACHE](LICENSE-APACHE) or
#   http://www.apache.org/licenses/LICENSE-2.0)
# * MIT license ([LICENSE-MIT](LICENSE-MIT) or
#   http://opensource.org/licenses/MIT)
#
# at your option.
#
# Unless you explicitly state otherwise, any contribution intentionally submitted
# for inclusion in the work by you, as defined in the Apache-2.0 license, shall
# be dual licensed as above, without any additional terms or conditions.
import os

TEMPLATE = '''
local description = |||
    {name}: basic description
|||;

function(wake)
    wake.declarePkg(
        fingerprint=import ".wake/fingerprint.json",
        namespace={namespace},
        name="{name}",
        version="0.1.0",
        description=description,
        paths=[
        ],
        pkgs= {
        },
        exports = function(wake, pkg) {
        },
    )
'''

def new_pkg(args):
    path = args.path
    name = args.name
    namespace = '"{}"'.format(args.namespace) if args.namespace else 'null'

    if path == None:
        raise ValueError("must provide path")

    if name == None:
        raise ValueError("must provide name")

    os.mkdir(path)
    with open(os.path.join(path, "PKG.libsonnet"), 'w') as f:
        f.write(TEMPLATE.format(name=name, namespace=namespace))
