

function(wake)
    local digest = import "./digest.json";
    local pkgVer = wake.pkgVer(null, "simple", "0.1.0", digest);

    wake.pkg(
        pkgVer = pkgVer,
    )
