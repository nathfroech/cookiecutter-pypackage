{% set is_open_source = cookiecutter.open_source_license != 'Not open source' -%}
{% for _ in cookiecutter.project_name %}={% endfor %}
{{ cookiecutter.project_name }}
{% for _ in cookiecutter.project_name %}={% endfor %}

{% if is_open_source %}
.. image:: https://img.shields.io/pypi/v/{{ cookiecutter.project_slug }}.svg
        :target: https://pypi.python.org/pypi/{{ cookiecutter.project_slug }}

.. image:: https://img.shields.io/travis/{{ cookiecutter.github_username }}/{{ cookiecutter.project_slug }}.svg
        :target: https://travis-ci.org/{{ cookiecutter.github_username }}/{{ cookiecutter.project_slug }}

.. image:: https://readthedocs.org/projects/{{ cookiecutter.project_slug | replace("_", "-") }}/badge/?version=latest
        :target: https://{{ cookiecutter.project_slug | replace("_", "-") }}.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status
{%- endif %}

.. image:: https://img.shields.io/badge/style-wemake-000000.svg
    :target: https://github.com/wemake-services/wemake-python-styleguide
    :alt: wemake.services code style

{% if cookiecutter.add_pyup_badge == 'y' %}
.. image:: https://pyup.io/repos/github/{{ cookiecutter.github_username }}/{{ cookiecutter.project_slug }}/shield.svg
     :target: https://pyup.io/repos/github/{{ cookiecutter.github_username }}/{{ cookiecutter.project_slug }}/
     :alt: Updates
{% endif %}


{{ cookiecutter.project_short_description }}

{% if is_open_source %}
* Free software: {{ cookiecutter.open_source_license }}
* Documentation: https://{{ cookiecutter.project_slug | replace("_", "-") }}.readthedocs.io.
{% endif %}

Getting started
---------------
{% if cookiecutter.use_environment_based_settings == 'y' -%}
Settings configuration
^^^^^^^^^^^^^^^^^^^^^^
All environment-dependent or confidential settings should be declared as environment variables. As an alternative, you
may create ``.env`` file at project root, which would contain all such variables.

Command ``make env_file`` will create such file with defaults, that should be replaced with actual values.

{%- endif %}
Updating requirements
^^^^^^^^^^^^^^^^^^^^^
Project uses `pip-tools
<https://github.com/jazzband/pip-tools>`_ for requirements management. If you need to add a new requirement, go to
``requirements`` directory and change the corresponding \*.in file. After that call ``make update_requirements`` to
compile \*.txt files and synchronize local environment.

For requirements installation in CI or production environments it is enough to simply call ``pip install -r
requirements/<file_name>.txt``.

For compatibility with traditional project structure there is also ``requirements.txt`` file at project root, which
simply links to ``requirements/production.txt``.

Linting
^^^^^^^

EditorConfig
============
There is ``.editorconfig`` file at the project root, which describes some basic rules for IDE. PyCharm supports it out
of the box, for other IDEs you may have to install a plugin.

Visit https://editorconfig.org/ for additional information.

Commit hooks
============
You may run linters after every commit so that they prevent committing code that has some problems. To do this, execute
``pre-commit install``.

This will install all hooks, described at configuration file ``.pre-commit-config.yaml``.

If you wish to run all checks manually, execute ``pre-commit run --all-files`` (or ``make lint``).
For running only a single specific check use ``pre-commit run <hook_id> --all-files`` (you can find hook id of the
desired check at ``.pre-commit-config.yaml``).

Note that ``pre-commit`` checks only files that are tracked by ``git``.

You can find tool documentation at https://pre-commit.com/.

Tests
^^^^^

Project uses ``pytest`` for testing.

All tests should be placed inside ``tests/`` directory and (ideally) follow the project structure - for example, tests
for ``{{cookiecutter.project_slug}}.some_package.some_module`` should be located at
``tests/some_package/test_some_module.py``

For assertions either default python's ``assert`` can be used, or more specific assertions from PyHamcrest_ - may be
useful for complex assertions and just more readable.

.. _PyHamcrest: https://pyhamcrest.readthedocs.io/en/release-1.8/library/

To run tests: ``make test``.
To run tests and receive a coverage statistics: ``make coverage``.


Features
--------

* TODO

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
