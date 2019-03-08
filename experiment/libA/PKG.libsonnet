function(wake) {
    local util = wake.util,

    result: wake.declarePkg(
        fingerprint=import ".wake/fingerprint.json",
        namespace=null,
        name="libA",
        version="1.0.0",
        pkgs= {
        },
        exports = function(wake, pkg) {
            adder(a, b):: a + b,
        },
    ),
}.result

