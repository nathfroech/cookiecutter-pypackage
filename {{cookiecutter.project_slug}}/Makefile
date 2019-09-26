.PHONY: docs help
.DEFAULT_GOAL := help

define BROWSER_PYSCRIPT
import os, webbrowser, sys

try:
	from urllib import pathname2url
except:
	from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

BROWSER := python -c "$$BROWSER_PYSCRIPT"

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

.PHONY: lint
lint:
	@pre-commit run --all-files

.PHONY: test
test: ## run tests quickly with the default Python
	@pytest -c setup.cfg

.PHONY: test-all
test-all: ## run tests on every Python version with tox
	tox

.PHONY: coverage
coverage: ## check code coverage quickly with the default Python
	@pytest -c setup.cfg --cov-config setup.cfg -s --cov-report term --cov {{ cookiecutter.project_slug }}

docs: ## generate Sphinx HTML documentation, including API docs
	rm -f docs/{{ cookiecutter.project_slug }}.rst
	rm -f docs/modules.rst
	sphinx-apidoc -o docs/ {{ cookiecutter.project_slug }}
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	$(BROWSER) docs/_build/html/index.html

servedocs: docs ## compile the docs watching for changes
	watchmedo shell-command -p '*.rst' -c '$(MAKE) -C docs html' -R -D .

release: dist ## package and upload a release
	twine upload dist/*

dist: clean ## builds source and wheel package
	python setup.py sdist
	python setup.py bdist_wheel
	ls -l dist

install: clean ## install the package to the active Python's site-packages
	python setup.py install

.PHONY: requirements
requirements:
	@bash helpers/update_requirements.sh

{%- if cookiecutter.use_environment_based_settings == 'y' -%}
.PHONY: env_file
env_file:
	@python helpers/generate_env_file.py
{%- endif %}

.PHONY: clean-build
clean-build: ## remove build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf .eggs/
	find . -name '*.egg-info' -delete
	find . -name '*.egg' -delete

.PHONY: clean-pyc
clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -delete
	find . -name '*.pyo' -delete
	## Files with tilde at the end of their name are backup files, created by some editors
	find . -name '*~' -delete
	find . -name '__pycache__' -delete

.PHONY: clean-test
clean-test: ## remove test and coverage artifacts
	rm -rf .tox/
	rm -f .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/

.PHONY: clean
clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

.PHONY: clean-ignored
clean-ignored: ## remove all files, listed in .gitignore
	git clean -fxd

.PHONY: clean-ignored-with-git
clean-ignored-with-git: clean-ignored ## remove all files, listed in .gitignore, and .git directory itself
	rm -rf .git/
