
function(wake) {
    local util = wake.util,

    result: wake.declarePkg(
        pkgInfo=wake.pkgInfo("foo1"),
        pkgs= {
            libA: wake.getPkg(wake.pkgInfo("libA")),
        },
        exports = function(wake, pkg) {
            local libA = pkg.pkgs.libA.exports,

            added: libA.add(5, 12),
        },
    ),
}.result
