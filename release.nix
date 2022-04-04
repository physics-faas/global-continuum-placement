{ hostPkgs ? import <nixpkgs> { }
, pinnedVersion ? hostPkgs.lib.importJSON ./nixpkgs-version.json
, pinnedPkgs ?
  hostPkgs.fetchFromGitHub {
    owner = "nixos";
    repo = "nixpkgs";
    inherit (pinnedVersion) rev sha256;
  }
, pkgs ? import pinnedPkgs { }
}:
let
  poetry2nix = pkgs.poetry2nix;
in
rec {
  package = poetry2nix.mkPoetryApplication {
    projectDir = ./.;
  };

  shell = let
    envShell = poetry2nix.mkPoetryEnv {
      projectDir = ./.;
    };
  in envShell.env;

  image = pkgs.callPackage ./deploy/docker.nix {
    global_continuum_placement = package;
  };
}
