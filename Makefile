.PHONY: install test

install:
	./install.sh

test:
	python3 scripts/validate-skills.py
	bash tests/test-install.sh
	bash skills/generate-html-report/scripts/test-init
