local wake = (import '../wake/wake.libsonnet');
local example = function(wake)
  wake.pkg(
    pkgName=wake.pkgName(null, 'simple')
  )
;

example(wake)
