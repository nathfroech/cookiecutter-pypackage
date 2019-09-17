# Change Log
All enhancements and patches to Cookiecutter PyPackage will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/).

## [Unreleased]
### Added
- Added `pip-tools` for requirements management (@nathfroech)
- Added `pre-commit` for running linters against commited changes (@nathfroech)
- Added `PyHamcrest` for test assertions (@nathfroech)
- Added option to use `environs` for environment-based settings (@nathfroech)
- Configured `mypy` (@nathfroech)
### Changed
- Updated `.editorconfig` content (@nathfroech)
- Made `pytest` mandatory (@nathfroech)
- Updated `flake8` configuration to rules based on
 [wemake.services linter](https://github.com/wemake-services/wemake-python-styleguide) (@nathfroech)
 - Removed additional checks for Python 2, added restriction for Python 3.6+ (@nathfroech)
 ### Removed
 - Removed parameter for setting author email (@nathfroech)

## [2019-05-09]
- Forked from original repository.
