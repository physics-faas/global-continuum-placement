{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-22.11";
    nix2container.url = "github:nlewo/nix2container";
    nix2container.inputs.nixpkgs.follows = "nixpkgs";
    flakeUtils.follows = "nix2container/flake-utils";
  };


  outputs = { self, nixpkgs, nix2container, flakeUtils }:
    let
      # Put the name of your service here
      myTool = "global-continuum-placement";

      buildDir = "/tmp/ryax/${myTool}";
      appDir = builtins.path { path = ./.; name = myTool; };
    in
    # Change values here to support more arch
    flakeUtils.lib.eachSystem [ "aarch64-linux" "x86_64-linux" ]
      (system:
        let
          pkgs = import nixpkgs { inherit system; };
          nix2containerPkgs = nix2container.packages.${system};
          python = pkgs.python3;
          lib = import ./nix/lib.nix { inherit pkgs python; };
        in
        {
          devShell = with nixpkgs; pkgs.mkShell {
            buildInputs = [ python3 pkgs.poetry ];
          };
          packages = {
            test = lib.test;
            lint = lib.lint;
            install = lib.install appDir buildDir;
            image = pkgs.callPackage ./nix/docker.nix {
              inherit myTool appDir;
              depsDir = (/. + buildDir);
              nix2container = nix2containerPkgs.nix2container;
            };
          };
          # Enable autoformat
          formatter = pkgs.nixpkgs-fmt;
        }
      );
}
