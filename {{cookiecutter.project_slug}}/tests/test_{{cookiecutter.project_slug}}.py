"""Tests for `{{ cookiecutter.project_slug }}` package."""
{%- if cookiecutter.command_line_interface|lower == 'click' %}
from click.testing import CliRunner
from hamcrest import assert_that, equal_to, is_, is_in

from {{ cookiecutter.project_slug }} import cli


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    script_result = runner.invoke(cli.main)
    assert_that(script_result.exit_code, is_(equal_to(0)))
    assert_that('{{ cookiecutter.project_slug }}.cli.main', is_in(script_result.output))


def test_command_line_interface_help():
    runner = CliRunner()
    help_result = runner.invoke(cli.main, ['--help'])
    assert_that(help_result.exit_code, is_(equal_to(0)))
    assert_that('--help  Show this message and exit.', is_in(help_result.output))
{%- endif %}
