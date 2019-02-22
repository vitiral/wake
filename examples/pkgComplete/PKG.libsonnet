
function(wake) wake.pkg(
    pkgInfo=wake.pkgInfo("foo1"),
    pkgs=[
        wake.getPkg(wake.pkgInfo("libA")),
    ],
)
