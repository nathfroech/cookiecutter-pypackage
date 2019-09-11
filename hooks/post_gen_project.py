import pathlib
import re
import shlex
import subprocess

PROJECT_DIRECTORY = pathlib.Path.cwd()


def remove_file(*filepath_terms: str):
    PROJECT_DIRECTORY.joinpath(*filepath_terms).unlink()


def clean_file_contents():
    """Clean generated files from trailing whitespaces and extra newlines."""
    for file_path in PROJECT_DIRECTORY.rglob('*'):
        if file_path.is_file():
            file_content = file_path.read_text()

            # Remove trailing whitespaces.
            file_content = re.sub(r'[ \t]+\n', '\n', file_content)
            # Python files may use two empty lines to separate code blocks (classes, etc.). Each particular case for
            # them will be checked by language-specific linters. For other files one empty line is enough.
            if file_path.suffix in {'.py'}:
                file_content = re.sub(r'\n{4,}', '\n\n\n', file_content, flags=re.MULTILINE)
            else:
                file_content = re.sub(r'\n{3,}', '\n\n', file_content, flags=re.MULTILINE)
            # Remove extra newlines before end of file.
            file_content = re.sub(r'\n{2,}\Z', '\n', file_content, flags=re.MULTILINE)

            file_path.write_text(file_content)


if __name__ == '__main__':

    if '{{ cookiecutter.create_author_file }}' != 'y':  # noqa: WPS308
        remove_file('AUTHORS.rst')
        remove_file('docs', 'authors.rst')

    if 'no' in '{{ cookiecutter.command_line_interface|lower }}':  # noqa: WPS308
        remove_file('{{ cookiecutter.project_slug }}', 'cli.py')

    if 'Not open source' == '{{ cookiecutter.open_source_license }}':  # noqa: WPS308
        remove_file('LICENSE')

    if '{{ cookiecutter.use_environment_based_settings }}' == 'y':  # noqa: WPS308
        dotenv_generator = PROJECT_DIRECTORY / 'helpers' / 'generate_env_file.py'
        subprocess.call(['python3', shlex.quote(str(dotenv_generator))])  # noqa: S607
    else:
        remove_file('helpers', 'generate_env_file.py')

    clean_file_contents()
