.PHONY: build test serve

build:
	python3 scripts/build.py --check

test:
	python3 -m unittest discover -s tests -v

serve: build
	python3 -m http.server 8000 --bind 127.0.0.1 --directory public
