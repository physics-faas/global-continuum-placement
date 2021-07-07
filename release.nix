{ nixpkgs ? import <nixpkgs> { } }:
let
  poetry2nix = nixpkgs.poetry2nix;
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

  image = nixpkgs.callPackage ./nix/docker.nix {
    global_continuum_placement = package;
  };
}
