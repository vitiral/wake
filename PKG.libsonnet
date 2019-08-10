local description = |||
    wake: awaken software development.

    Wake is a new kind of package manager. It aims to bring distributed package management,
    build systems and configuration management into the hands of anyone at any scale.
|||;

function(wake)
    local pkgVer = wake.pkgVer(
        namespace=null,
        name="wake",
        version="0.1.0",
        fingerprint=import ".wake/fingerprint.json",
    );

    W.declarePkg(
        pkgVersion=pkgVersion,
        description=description,
        paths=[
            "./wake",
        ],
        localPkgs = {
        },
        deps = {
            # W.pkgReq(null, "echo", "1.2.3"),
            libA: W.getPkg(W.pkgReq(null, "libA"), from="./experiment/libA"),
        },
        exports = function(W, pkg) {
            # local libA = pkg.pkgs.libA.exports,

            answer: 42,
            # added: libA.adder(1, 2),
        },
    )
