function(wake)
    local digest = import "./.wakeDigest.json";
    local pkgVer = wake.pkgVer(null, "libA", "5.5.0", digest);

    wake.pkg(
        pkgVer = pkgVer,
        export = function(wake, pkg) {
            answer: 42,
        },
    )
