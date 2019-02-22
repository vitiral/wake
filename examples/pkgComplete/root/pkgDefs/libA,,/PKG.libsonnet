function(wake) {
    result: wake.pkg(
        pkgInfo = wake.pkgInfo("libA"),
        pkgs = null,
        exports = function(wake, pkg) {
            add(a, b):: a + b,
        }
    )
}.result
