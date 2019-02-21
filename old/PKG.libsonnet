local wake = import "wake.libsonnet";

function(wake) { 
    result: wake.pkg(
        name = "hello",
        version = "0.1",
    )
}
