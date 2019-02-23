local meta = import "PKG.meta";

function(wake) {
    local util = wake.util,

    result: wake.declarePkg(
        hash=meta.hash,
        name="libA",
        version="1.0.0",
        pkgs= {
        },
        exports = function(wake, pkg) {
            adder(a, b):: a + b,
        },
    ),
}.result

