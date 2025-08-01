
set shell := [ 
	"nix",
	"develop",
	"--command",
	"bash", 
	"-c",
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
