function(wake)
    local util = wake.util;
    local getFakePath = "./getFake.py";

    wake.declarePkg(
        fingerprint=import ".wake/fingerprint.json",
        namespace=null,
        name="libA",
        version="1.0.0",
        pkgs= {
        },
        paths=[
            getFakePath,
            "./data.txt",
        ],
        exports = function(wake, pkg) {
            adder(a, b):: a + b,
            getFake: wake.exec(
                pathRef=wake.pathRef(pkg, getFakePath),
                container=wake.EXEC_LOCAL,
            ),
        },
    )
