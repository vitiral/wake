local meta = import "PKG.meta";

function(wake) {
    local util = wake.util,

    result: wake.declarePkg(
        hash=meta.hash,
        name="wake",
        version="0.1.0",
        paths=[
            "./wake",
        ],
        pkgs= {
            libA: wake.getPkg(wake.pkgReq("libA"), from="./experiment/libA"),
        },
        exports = function(wake, pkg) {
            answer: 42,
            // added: TODO,
        },
    ),
}.result
