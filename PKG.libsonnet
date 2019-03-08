local description = |||
    wake: awaken software development.

    Wake is a new kind of package manager. It aims to bring distributed package management,
    build systems and configuration management into the hands of anyone at any scale.
|||;

function(wake)
    wake.declarePkg(
        fingerprint=import ".wake/fingerprint.json",
        namespace=null,
        name="wake",
        version="0.1.0",
        description=description,
        paths=[
            "./wake",
        ],
        pkgs= {
            libA: wake.getPkg(wake.pkgReq(null, "libA"), from="./experiment/libA"),
        },
        exports = function(wake, pkg) {
            answer: 42,
            // added: TODO,
        },
    )
