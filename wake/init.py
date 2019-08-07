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
