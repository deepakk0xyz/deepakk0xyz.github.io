{
  description = "A very basic flake";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs";
  };

  outputs = { nixpkgs, ... }:
    let
      system = "x86_64-linux";
			pkgs = nixpkgs.legacyPackages.${system};
    in {
			devShells.${system}.default = pkgs.mkShellNoCC {
				packages = with pkgs; [
					nodejs
					nodePackages.npm
					python3
					python313Packages.requests
					python313Packages.pyyaml
					python313Packages.beautifulsoup4
					texliveFull
				];
			};
    };
}
