
local paths = [
    "./README.txt",
    "./script.py",
];


function(wake)
    local digest = import "./.wakeDigest.json";
    local pkgVer = wake.pkgVer(null, "file_paths", "0.1.0", digest);

    wake.pkg(
        pkgVer = pkgVer,
        paths = paths,
        deps = wake.deps(
            unrestricted={
                "pytest": "pYpI@pytest@>=5.0.0",
            },
        ),
    )

