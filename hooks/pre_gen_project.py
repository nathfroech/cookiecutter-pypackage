import re
import sys

MODULE_REGEX = r'^[_a-zA-Z][_a-zA-Z0-9]+$'

module_name = '{{ cookiecutter.project_slug}}'

WARNING_TEMPLATE = '\x1b[1;33m [WARNING]: {0} \x1b[0m'

python_major_version = sys.version_info[0]
if python_major_version == 2:
    print(WARNING_TEMPLATE.format(  # noqa: T001
        "You're running cookiecutter under Python 2, but the generation scripts and "
        'generated project require Python 3.6+. Generation process stopped.',
    ))
    sys.exit(1)
elif python_major_version == 3 and sys.version_info[1] < 6:
    print(WARNING_TEMPLATE.format(  # noqa: T001
        "You're running cookiecutter under Python 3.5 or lower, but the generation scripts and "
        'generated project require Python 3.6+. Generation process stopped.',
    ))
    sys.exit(1)

if not re.match(MODULE_REGEX, module_name):
    print(WARNING_TEMPLATE.format(  # noqa: T001
        'The project slug ({0}) is not a valid Python module name. '
        'Please do not use a - and use _ instead'.format(module_name),
    ))

    # Exit to cancel project
    sys.exit(1)
