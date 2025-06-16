{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };

        pythonEnv =
          pkgs.python312.withPackages (ps: with ps; [ tqdm requests numpy ]);
      in {
        devShells.default = pkgs.mkShell {
          buildInputs = [ pythonEnv ];
          shellHook = ''
            exec ${pkgs.fish}/bin/fish
          '';
        };

      });
}
