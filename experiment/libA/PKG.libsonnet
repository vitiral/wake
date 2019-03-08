function(wake)
    local util = wake.util;

    wake.declarePkg(
        fingerprint=import ".wake/fingerprint.json",
        namespace=null,
        name="libA",
        version="1.0.0",
        pkgs= {
        },
        paths=[
            "./data.txt",
        ],
        exports = function(wake, pkg) {
            adder(a, b):: a + b,
        },
    )
