{
  dockerTools,
  ryaxBaseImage,
  ryaxBaseImageConfig,
  global_continuum_placement,
  # Deploy script dependencies
  pythonPackages,
  tag ? "latest",
}:
dockerTools.buildImage {
  name = "physics-global-continuum-placement";
  inherit tag;
  contents = [ global_continuum_placement ];

  fromImage = ryaxBaseImage;

  config = ryaxBaseImageConfig // {
    EntryPoint = [ "/bin/pgcp" ];
    Env = [
      "TMP_DIR=/tmp"
    ];
  };
}
