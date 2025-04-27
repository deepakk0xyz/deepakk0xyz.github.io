let
  pkgs = import <nixpkgs> { };
in
  pkgs.stdenv.mkDerivation {
    name = "deepakk.xyz";
    src = ./src;
    buildInputs = with pkgs; [
      texliveFull
      pandoc
    ];

    buildPhase = ''
      mkdir -p $out

      pushd $src
      for file in $(find . -type f); do
        base=$(basename $file)
        name=''${base%.*}
        extension=''${base##*.}
        pandoc $file -t html -s -o $out/''${name}.html
        pandoc $file -t pdf -s -o $out/''${name}.pdf
      done
      popd
    '';
  }