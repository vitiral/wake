
function(wake) {
    local util = wake.util,

    result: wake.declarePkg(
        hash="ae92kd",
        name="pkgComplete",
        version="1.0.0",
        pkgs= {
            libA: wake.getPkg(wake.pkgReq("libA")),
        },
        exports = function(wake, pkg) {
            local libA = pkg.pkgs.libA.exports,

            added: libA.add(5, 12),
        },
    ),
}.result
