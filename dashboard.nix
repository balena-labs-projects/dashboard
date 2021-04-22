{ pkgs ? import <nixpkgs> {} }:

with pkgs;

dockerTools.buildImage {
  name = "grafana";
  contents = [pkgs.grafana
              pkgs.bashInteractive
              (pkgs.python3.withPackages (pkgs: with pkgs; [
              stringcase
              ]))
             ];
}

