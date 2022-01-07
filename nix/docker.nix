{
  dockerTools,
  global_continuum_placement,
  # Deploy script dependencies
  pythonPackages,
  tag ? "latest",
}:
dockerTools.buildImage {
  name = "physics-global-continuum-placement";
  inherit tag;
  contents = [ global_continuum_placement ];

  config = {
    EntryPoint = [ "/bin/pgcp" ];
    Env = [
      "TMP_DIR=/tmp"
    ];
  };
}
