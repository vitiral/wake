function(wake) {
    local util = wake.util,

    result: wake.declarePkg(
        fingerprint=import ".wake/fingerprint.json",
        name="wake",
        version="0.1.0",
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
    ),
}.result
