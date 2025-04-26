let
  pkgs = import <nixpkgs> { };
in
  pkgs.stdenv.mkDerivation {
    name = "deepakk.xyz";
    src = ./src;
    buildInputs = with pkgs; [
      texliveMedium
      pandoc
    ];

    buildPhase = ''
      mkdir -p $out
      cd $src
      find . -type f | xargs -I {} pandoc {} -t html -s -o $out/{}.html
    '';
  }