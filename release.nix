{ nixpkgs ? import <nixpkgs> { } }:
let
  poetry2nix = nixpkgs.poetry2nix;
in
rec {
  package = poetry2nix.mkPoetryApplication {
    projectDir = ./.;
    inherit (ryaxpkgs) python;
  };

  shell = let
    envShell = poetry2nix.mkPoetryEnv {
      projectDir = ./.;
    };
  in envShell.env;

  image = ryaxpkgs.callPackage ./nix/docker.nix {
    global_continuum_placement = package;
  };
}
