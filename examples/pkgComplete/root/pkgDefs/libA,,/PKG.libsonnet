function(wake) {
    result: wake.pkg(
        pkgInfo = wake.pkgInfo("libA"),
        pkgs = [],
        exports = {
            add(a, b):: a + b,
        }
    )
}.result
