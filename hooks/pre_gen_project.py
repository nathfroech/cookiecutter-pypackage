import re
import sys

MODULE_REGEX = r'^[_a-zA-Z][_a-zA-Z0-9]+$'

module_name = '{{ cookiecutter.project_slug}}'

if not re.match(MODULE_REGEX, module_name):
    print(  # noqa: T001
        'ERROR: The project slug ({0}) is not a valid Python module name. '
        'Please do not use a - and use _ instead'.format(module_name),
    )

    # Exit to cancel project
    sys.exit(1)
