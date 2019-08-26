
local paths = [
    "./README.txt",
    "./script.py",
];


function(wake)
    local digest = import "./.wakeDigest.json";
    local pkgVer = wake.pkgVer(null, "file_paths", "0.1.0", digest);

    wake.pkg(
        pkgVer=pkgVer,
        paths=paths,
        deps=wake.deps(
            unrestricted={
                "libA": wake.pkgReq("fake", "libA", ">=5.2.0"),
            },
        ),

        export=function(wake, pkg)
            local libA = pkg.deps.unrestricted.libA;

            {
                libA_export: libA.export,
                libA_answer: libA.export.answer,
                answer: self.libA_answer / 6,
            }
    )
