function(wake) {
    result: wake.declarePkg(
        pkgInfo = wake.pkgInfo("libA"),
        pkgs = null,
        exports = function(wake, pkg) {
            add(a, b):: a + b,
        }
    )
}.result
