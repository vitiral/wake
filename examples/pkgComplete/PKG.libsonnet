
function(wake) wake.pkg(
    wake=wake,
    pkgInfo=wake.pkgInfo("foo1"),
    pkgs=[
        wake.getPkg(wake, wake.pkgInfo("libA")),
    ],
)
