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
      for file in $(find $src -type f -not -path "$src/templates/*"); do
        basename=$(basename $file)
        name=''${basename%.*}
        extension=''${file##*.}
        outpath=$(dirname $out/$(realpath -s --relative-to="$src" $file))
        mkdir -p $outpath

        pandoc $file -t html -s -o $outpath/$name.html

        if [ $extension = "tex" ]; then
          pdflatex $file
          cp $name.pdf $outpath/$name.pdf
        fi
      done
    '';
  }