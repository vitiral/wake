function(wake) {
    local util = wake.util,

    result: wake.declarePkg(
        hash="ae92kd",
        name="wake",
        version="0.1.0",
        pkgs= {
            // libA: wake.getPkg(wake.pkgReq("libA")),
        },
        exports = function(wake, pkg) {
            answer: 42
        },
    ),
}.result
