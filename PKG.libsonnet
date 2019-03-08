local description = |||
    wake: awaken software development.

    Wake is a new kind of package manager. It aims to bring distributed package management,
    build systems and configuration management into the hands of anyone at any scale.
|||;

function(W)
    W.declarePkg(
        fingerprint=import ".wake/fingerprint.json",
        namespace=null,
        name="wake",
        version="0.1.0",
        description=description,
        paths=[
            "./wake",
        ],
        pkgs = {
            libA: W.getPkg(W.pkgReq(null, "libA"), from="./experiment/libA"),
            echo: W.getPkg(
                W.pkgReq(null, "echo", "1.2.3"),
                from='getEchoer',
                usingPkg='libA'
            ),
        },
        exports = function(W, pkg) {
            local libA = pkg.pkgs.libA.exports,

            answer: 42,
            added: libA.adder(1, 2),
        },
    )
