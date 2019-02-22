{
    local W = self,

    user(name, email=null): {
        name: name,
        email: email,
    },

    pkgInfo(name, version=null, namespace=null):
        '%s|%s|%s' %[
            name,
            if version == null then "*" else version,
            W.util.stringDefault(namespace),
        ],

    getPkg(wake, key): {
        return: if key in wake.pkgs then
            wake.pkgs[key]
        else
            null,
    }.return,

    pkg(wake, pkgInfo, pkgs=null): {
        pkgInfo: pkgInfo,
        pkgs: [
            wake.getPkg(wake, p)
            for p in W.util.arrayDefault(pkgs)
        ],
    },

    util: {
        arrayDefault(arr): if arr == null then [] else arr,
        stringDefault(s): if s == null then "" else s
    },
}
