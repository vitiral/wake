
function(wake) {
    local util = wake.util,

    result: wake.pkg(
        pkgInfo=wake.pkgInfo("foo1"),
        pkgs= {
            libA: wake.getPkg(wake.pkgInfo("libA")),
        },
        exports = function(wake, pkg) {
            local libA = pkg.pkgs.libA,

            added: if util.isCompleted(libA) then
                libA.exports.add(5, 12) 
                else util.unresolved(),
        },
    ),
}.result
