
set shell := [ 
	"nix",
	"develop",
	"--command",
	"bash", 
	"-c",
]

start:
	just install
	npx @11ty/eleventy --serve

alias run := start

build:
	just install
	npx @11ty/eleventy

install:
	npm install

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
