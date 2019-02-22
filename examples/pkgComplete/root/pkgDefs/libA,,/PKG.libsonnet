function(wake) {
    result: wake.pkg(
        pkgInfo = wake.pkgInfo("libA"),
        pkgs = null,
        exports = {
            add(a, b):: a + b,
        }
    )
}.result
