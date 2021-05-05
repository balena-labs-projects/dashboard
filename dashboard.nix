# { system ? builtins.currentSystem }:

# let pkgs = import <nixpkgs> { inherit system; };

# in with pkgs;
# { pkgs ? import <nixpkgs> { system = "armv7l-linux"; } }:

# let pkgs = import <nixpkgs> {
#     crossSystem = (import <nixpkgs/lib>).systems.examples.armv7l-hf-multiplatform;
# };

let pkgs = import <nixpkgs> {
  crossSystem = {
    config = "armv7l-unknown-linux-gnueabihf";
  };
};

in pkgs.dockerTools.buildImage {
  name = "dashboard";
  contents = [
              pkgs.grafana
              pkgs.bashInteractive
              (pkgs.python3.withPackages (pkgs: with pkgs; [
              stringcase
              ]))
             ];
}

