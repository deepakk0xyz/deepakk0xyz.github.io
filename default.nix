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
        echo "File: $file"
        basename=$(basename $file)
        name=''${basename%.*}
        extension=''${file##*.}
        outpath="$(dirname $out/$(realpath -s --relative-to="$src" $file))"
        mkdir -p "$outpath"

        if [ $extension = "md" ]; then
          pandoc "$file" -t html -s -o "$outpath/$name.html"
        fi

        if [ $extension = "pdf" ]; then
          cp "$file" "$outpath/$name.pdf"
        fi
      done
    '';
  }