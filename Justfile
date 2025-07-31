
set shell := [ 
	"nix-shell",
	"-p",
	"nodejs",
	"nodePackages.npm",
	"python3",
	"python313Packages.requests",
	"python313Packages.pyyaml",
	"python313Packages.beautifulsoup4",
  "texliveFull",
	"--run"
]

start:
  npx @11ty/eleventy --serve

alias run := start

build:
  npx @11ty/eleventy

update:
	npm update

shell:
	$SHELL

imdb *ARGS:
	python3 ./scripts/imdb.py {{ARGS}}

books *ARGS:
	python3 ./scripts/books.py {{ARGS}}

latex:
	find . -name "main.tex" | xargs pdflatex
	just build
