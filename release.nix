{ ryaxpkgs ? import <ryaxpkgs> { } }:
let
  poetry2nix = ryaxpkgs.pkgs.poetry2nix;
  overrides = poetry2nix.overrides.withDefaults (self: super: {
    # Fixes https://github.com/pytest-dev/pytest/issues/7891
    pytest = super.pytest.overrideAttrs (old: {
      postPatch = old.postPatch or "" + ''
        sed -i '/\[metadata\]/aversion = ${old.version}' setup.cfg
      '';
    });
    # Fixes https://github.com/nix-community/poetry2nix/issues/123
    importlib-metadata = super.importlib-metadata.overrideAttrs (old: {
      postPatch = old.postPatch or "" + ''
        sed -i '/\[metadata\]/aversion = ${old.version}' setup.cfg
      '';
    });
  });
in
rec {
  package = poetry2nix.mkPoetryApplication {
    projectDir = ./.;
    inherit overrides;
    inherit (ryaxpkgs) python;
  };

  shell = let
    envShell = poetry2nix.mkPoetryEnv {
      projectDir = ./.;
      inherit (ryaxpkgs) python;
      inherit overrides;
    };
  in envShell.env;

  docs = ryaxpkgs.buildSphinxDoc {
    inherit package;
  };

  image = ryaxpkgs.callPackage ./nix/docker.nix {
    CHANGEME = package;
  };
}
