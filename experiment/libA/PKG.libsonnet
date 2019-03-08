function(wake)
    local util = wake.util;
    local getEchoerPath = "./getEchoer.py";

    wake.declarePkg(
        fingerprint=import ".wake/fingerprint.json",
        namespace=null,
        name="libA",
        version="1.0.0",
        pkgs= {
        },
        paths=[
            getEchoerPath,
            "./data.txt",
        ],
        exports = function(wake, pkg) {
            adder(a, b):: a + b,
            getEchoer: wake.exec(
                pathRef=wake.pathRef(pkg, getEchoerPath),
                container=wake.EXEC_LOCAL,
            ),
        },
    )
