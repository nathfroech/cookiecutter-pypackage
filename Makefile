BAKE_OPTIONS=--no-input

help:
	@echo "bake 	generate project using defaults"
	@echo "watch 	generate project using defaults and watch for changes"
	@echo "replay 	replay last cookiecutter run and watch for changes"

bake:
	cookiecutter $(BAKE_OPTIONS) . --overwrite-if-exists

watch: bake
	watchmedo shell-command -p '*.*' -c 'make bake -e BAKE_OPTIONS=$(BAKE_OPTIONS)' -W -R -D \{{cookiecutter.project_slug}}/

replay: BAKE_OPTIONS=--replay
replay: watch
	;

.PHONY: requirements
requirements:
	@bash helpers/update_requirements.sh

.PHONY: test
test:
	@pytest -c setup.cfg

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
