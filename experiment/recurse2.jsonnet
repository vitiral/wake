// we want to actually compute some things here

{
    local this = self,

    local wake = {
        local W = wake,

        globals: {
            "key1": 1,
            "key2": "foobar",

            // note: this must be guaranteed to succeed before
            // it can be added to globlas. Hence why globlas
            // must be evaluated only after the pkg is completed.
            "dPkg": W.getPkg(W, "pkgD"),
        },

        pkgs: {
            pkgB: W.pkg(W, "b"),
            pkgC: W.pkg(
                W, "c",
                pkgs = ["pkgD"]
            ),
            pkgD: W.pkg(W, "d"),
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
                for p in wake.util.arrayDefault(pkgs)
            ],
        },

        util: {
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

