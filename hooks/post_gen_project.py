#!/usr/bin/env python
import pathlib
import re

PROJECT_DIRECTORY = pathlib.Path.cwd()


def remove_file(*filepath_terms: str):
    PROJECT_DIRECTORY.joinpath(*filepath_terms).unlink()


def clean_file_contents():
    """Clean generated files from trailing whitespaces and extra newlines."""
    for file_path in PROJECT_DIRECTORY.rglob('*'):
        if file_path.is_file():
            content = file_path.read_text()

            # Remove trailing whitespaces.
            content = re.sub(r'[ \t]+\n', '\n', content)
            # Python files may use two empty lines to separate code blocks (classes, etc.). Each particular case for
            # them will be checked by language-specific linters. For other files one empty line is enough.
            if file_path.suffix in ('.py',):
                content = re.sub(r'\n{4,}', '\n\n\n', content, flags=re.MULTILINE)
            else:
                content = re.sub(r'\n{3,}', '\n\n', content, flags=re.MULTILINE)
            # Remove extra newlines before end of file.
            content = re.sub(r'\n{2,}\Z', '\n', content, flags=re.MULTILINE)

            file_path.write_text(content)


if __name__ == '__main__':

    if '{{ cookiecutter.create_author_file }}' != 'y':
        remove_file('AUTHORS.rst')
        remove_file('docs', 'authors.rst')

    if 'no' in '{{ cookiecutter.command_line_interface|lower }}':
        remove_file('{{ cookiecutter.project_slug }}', 'cli.py')

    if 'Not open source' == '{{ cookiecutter.open_source_license }}':
        remove_file('LICENSE')

    clean_file_contents()
