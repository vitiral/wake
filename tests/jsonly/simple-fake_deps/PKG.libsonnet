
local paths = [
    "./README.txt",
    "./script.py",
];


function(wake)
    local digest = import "./.wakeDigest.json";
    local pkgVer = wake.pkgVer(null, "simple-fake_deps", "0.1.0", digest);

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
                int: 3,
                libA_export: libA.export,
                libA_answer: libA.export.answer,
                final_answer: self.libA_answer / 6,
            },
    )
