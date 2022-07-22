#!/usr/bin/env bash
export NIXOS_VERSION=${NIXOS_VERSION:="22.05"}

nix-prefetch-git \
    https://github.com/nixos/nixpkgs.git refs/heads/nixos-${NIXOS_VERSION} \
    > nixpkgs-version.json
