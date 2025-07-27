
set shell := [ "nix-shell", "-p", "nodejs", "nodePackages.npm", "--run"]

start:
  npx @11ty/eleventy --serve

alias run := start

build:
  npx @11ty/eleventy

update:
	npm update

shell:
	$SHELL
