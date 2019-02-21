
{
    local this = self,

    local pkg(name, pkgs=null) = {
        name: name,
        pkgs: pkgs,
    },

    local recursePkg(pkg) = {
        local pkgs = if pkg.pkgs == null then
            []
        else
            pkg.pkgs,

        return: [pkg] + [recursePkg(p) for p in pkgs],
    }.return,

    pkgA: pkg("a", pkgs = [pkgB, pkgC]),
    local pkgB = pkg("b"),
    local pkgC = pkg("c", pkgs = [pkgD]),
    local pkgD = pkg("d"),

    return: recursePkg(this.pkgA),
}.return
