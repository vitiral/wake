// we want to actually compute some things here

{
    local this = self,

    local wake = {
        local w = wake,

        pkgs: {
            pkgB: w.pkg(w, "b"),
            pkgC: w.pkg(
                w, "c",
                pkgs = ["pkgD"]
            ),
            pkgD: w.pkg(w, "d"),
        },

        getPkg(wake, key): {
            return: if key in wake.pkgs then
                wake.pkgs[key]
            else
                null,
        }.return,

        pkg(wake, name, pkgs=null): {
            name: name,
            pkgs: [
                wake.getPkg(wake, p)
                for p in wake.helpers.arrayDefault(pkgs)
            ],
        },

        helpers: {
            arrayDefault(arr): if arr == null then
                []
            else
                arr,
        },
    },

    pkgA: wake.pkg(
        wake, "a", 
        pkgs = ['pkgB', 'pkgC']
    ),

    a: "foo",

    local recursePkg(pkg) = {
        local pkgs = if pkg.pkgs == null then
            []
        else
            pkg.pkgs,

        return: [pkg] + [recursePkg(p) for p in pkgs],
    }.return,


    return: recursePkg(this.pkgA),
}

