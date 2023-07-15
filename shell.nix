{ pkgs ? import (fetchTarball
  "https://github.com/NixOS/nixpkgs/archive/refs/tags/23.05.tar.gz") { } }:

pkgs.mkShell {
  buildInputs =
    [ pkgs.python311 pkgs.poetry pkgs.nixfmt pkgs.lolcat pkgs.which ];
}
