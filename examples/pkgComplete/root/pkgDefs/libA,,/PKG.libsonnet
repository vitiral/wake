function(wake) {
    result: wake.declarePkg(
        hash="ABAAB",
        name="libA",
        version="1.0.0",
        pkgs = null,
        exports = function(wake, pkg) {
            add(a, b):: a + b,
        }
    )
}.result
