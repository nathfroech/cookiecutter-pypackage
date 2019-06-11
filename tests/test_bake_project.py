import datetime
import os
import pathlib
import shlex
import subprocess
import sys
from contextlib import contextmanager
from typing import Tuple

import pytest
import sh
import yaml
from click.testing import CliRunner
from cookiecutter.utils import rmtree
from hamcrest import assert_that, equal_to, has_key, is_, is_in, none, not_
from pytest_cases import pytest_fixture_plus

import settings

if sys.version_info > (3, 0):
    import importlib  # noqa: Z435
else:
    import imp  # noqa: Z435


@contextmanager
def inside_dir(dirpath):
    """
    Execute code from inside the given directory.

    :param dirpath: String, path of the directory the command is being run.
    """
    old_path = os.getcwd()
    try:  # noqa: Z437
        os.chdir(dirpath)
        yield
    finally:
        os.chdir(old_path)


@contextmanager
def bake_in_temp_dir(cookies, *args, **kwargs):
    """
    Delete the temporal directory that is created when executing the tests.

    :param cookies: pytest_cookies.Cookies,
        cookie to be baked and its temporal files will be removed
    """
    baked_result = cookies.bake(*args, **kwargs)
    try:  # noqa: Z437
        yield baked_result
    finally:
        rmtree(str(baked_result.project))


def run_inside_dir(command, dirpath):
    """
    Run a command from inside a given directory, returning the exit status.

    :param command: Command that will be executed
    :param dirpath: String, path of the directory the command is being run.
    """
    with inside_dir(dirpath):
        return subprocess.check_call(shlex.split(command))


def check_output_inside_dir(command, dirpath):
    """Run a command from inside a given directory, returning the command output."""
    with inside_dir(dirpath):
        return subprocess.check_output(shlex.split(command))


def test_year_compute_in_license_file(cookies):
    with bake_in_temp_dir(cookies) as baked_result:
        license_file_path = pathlib.Path(baked_result.project) / 'LICENSE'
        now = datetime.datetime.now()
        assert_that(str(now.year), is_in(license_file_path.read_text()))


def project_info(baked_result) -> Tuple[pathlib.Path, str, pathlib.Path]:
    """Get toplevel dir, project_slug, and project dir from baked cookies."""
    project_path = pathlib.Path(baked_result.project)
    project_slug = project_path.name
    project_dir = project_path / project_slug
    return project_path, project_slug, project_dir


def test_bake_with_defaults(cookies):
    with bake_in_temp_dir(cookies) as baked_result:
        project_path = pathlib.Path(baked_result.project)
        assert_that(project_path.is_dir())
        assert_that(baked_result.exit_code, is_(equal_to(0)))
        assert_that(baked_result.exception, is_(none()))

        assert_that(project_path.joinpath('setup.py').is_file())
        assert_that(project_path.joinpath('python_boilerplate').is_dir())
        assert_that(project_path.joinpath('tox.ini').is_file())
        assert_that(project_path.joinpath('tests').is_dir())


@pytest.mark.parametrize('name', [
    pytest.param('Alice Liddell', id='simple_name'),
    pytest.param('something-with-a-dash', id='name_with_dashes'),
    pytest.param('name "quote" name', id='name_with_quotes'),
    pytest.param("O'connor", id='name_with_apostrophe'),
])
def test_bake_and_run_tests(name, cookies):
    """Ensure that a `full_name` with certain symbols does not break setup.py."""
    with bake_in_temp_dir(cookies, extra_context={'full_name': name}) as baked_result:
        project_path = pathlib.Path(baked_result.project)
        assert_that(project_path.is_dir())
        test_file_path = project_path / 'tests' / 'test_python_boilerplate.py'
        assert_that(test_file_path.is_file())
        tests_exit_code = run_inside_dir('make test', str(project_path))
        assert_that(tests_exit_code, is_(equal_to(0)))


def test_bake_without_travis_pypi_setup(cookies):
    with bake_in_temp_dir(cookies, extra_context={'use_pypi_deployment_with_travis': 'n'}) as baked_result:
        project_path = pathlib.Path(baked_result.project)
        result_travis_config = yaml.full_load(project_path.joinpath('.travis.yml').open())
        assert_that(result_travis_config, not_(has_key('deploy')))
        assert_that(result_travis_config['language'], is_(equal_to('python')))


def test_bake_without_author_file(cookies):
    with bake_in_temp_dir(cookies, extra_context={'create_author_file': 'n'}) as baked_result:
        project_path = pathlib.Path(baked_result.project)

        assert_that(not project_path.joinpath('AUTHORS.rst').exists())
        assert_that(not project_path.joinpath('docs', 'authors.rst').exists())

        # Assert there are no spaces in the toc tree
        docs_index_path = project_path / 'docs' / 'index.rst'
        assert_that('contributing\n   history', is_in(docs_index_path.read_text()))

        # Check that
        manifest_path = project_path / 'MANIFEST.in'
        assert_that('AUTHORS.rst', not_(is_in(manifest_path.read_text())))


def test_make_help(cookies):
    with bake_in_temp_dir(cookies) as baked_result:
        output = check_output_inside_dir('make help', str(baked_result.project))
        assert_that(b'check code coverage quickly with the default Python', is_in(output))


@pytest.mark.parametrize('license_name,target_string', [
    pytest.param('MIT license', 'MIT ', id='mit'),
    pytest.param(
        'BSD license',
        'Redistributions of source code must retain the above copyright notice, this',
        id='bsd',
    ),
    pytest.param('ISC license', 'ISC License', id='isc'),
    pytest.param('Apache Software License 2.0', 'Licensed under the Apache License, Version 2.0', id='apache'),
    pytest.param('GNU General Public License v3', 'GNU GENERAL PUBLIC LICENSE', id='gnu'),
])
def test_bake_selecting_license(license_name, target_string, cookies):
    with bake_in_temp_dir(cookies, extra_context={'open_source_license': license_name}) as baked_result:
        project_path = pathlib.Path(baked_result.project)
        assert_that(target_string, is_in(project_path.joinpath('LICENSE').read_text()))
        assert_that(license_name, is_in(project_path.joinpath('setup.py').read_text()))


def test_bake_not_open_source(cookies):
    with bake_in_temp_dir(cookies, extra_context={'open_source_license': 'Not open source'}) as baked_result:
        project_path = pathlib.Path(baked_result.project)
        assert_that(project_path.joinpath('setup.py').is_file())
        assert_that(not project_path.joinpath('LICENSE').exists())
        assert_that('License', not_(is_in(project_path.joinpath('README.rst').read_text())))


def test_bake_with_no_console_script(cookies):
    context = {'command_line_interface': 'No command-line interface'}
    baked_result = cookies.bake(extra_context=context)
    project_path, project_slug, project_dir = project_info(baked_result)
    assert_that(not project_dir.joinpath('cli.py').exists())
    assert_that('entry_points', not_(is_in(project_path.joinpath('setup.py').read_text())))


def test_bake_with_console_script_files(cookies):
    context = {'command_line_interface': 'click'}
    baked_result = cookies.bake(extra_context=context)
    project_path, project_slug, project_dir = project_info(baked_result)

    assert_that(project_dir.joinpath('cli.py').is_file())
    assert_that('entry_points', is_in(project_path.joinpath('setup.py').read_text()))


def test_bake_with_console_script_cli(cookies):  # noqa: Z210
    context = {'command_line_interface': 'click'}
    baked_result = cookies.bake(extra_context=context)
    project_path, project_slug, project_dir = project_info(baked_result)
    module_path = str(project_dir / 'cli.py')
    module_name = '{0}.{1}'.format(project_slug, 'cli')
    if sys.version_info >= (3, 5):
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        cli = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cli)
    elif sys.version_info >= (3, 3):
        file_loader = importlib.machinery.SourceFileLoader
        cli = file_loader(module_name, module_path).load_module()
    else:
        cli = imp.load_source(module_name, module_path)
    runner = CliRunner()
    noarg_result = runner.invoke(cli.main)
    assert_that(noarg_result.exit_code, is_(equal_to(0)))
    noarg_output = ' '.join(['Replace this message by putting your code into', project_slug])
    assert_that(noarg_output, is_in(noarg_result.output))
    help_result = runner.invoke(cli.main, ['--help'])
    assert_that(help_result.exit_code, is_(equal_to(0)))
    assert_that('Show this message', is_in(help_result.output))


YN_CHOICES = ['y', 'n']
LICENSE_CHOICES = [
    'MIT license',
    'BSD license',
    'ISC license',
    'Apache Software License 2.0',
    'GNU General Public License v3',
    'Not open source',
]


@pytest_fixture_plus  # noqa: Z216
@pytest.mark.parametrize('use_pypi_deployment_with_travis', YN_CHOICES, ids=lambda yn: 'pypi_travis:{0}'.format(yn))
@pytest.mark.parametrize('add_pyup_badge', YN_CHOICES, ids=lambda yn: 'pyup:{0}'.format(yn))
@pytest.mark.parametrize(
    'command_line_interface',
    ['Click', 'No command-line interface'],
    ids=lambda yn: 'cli:{0}'.format(yn.lower()),
)
@pytest.mark.parametrize('create_author_file', YN_CHOICES, ids=lambda yn: 'author:{0}'.format(yn))
@pytest.mark.parametrize(
    'open_source_license',
    LICENSE_CHOICES,
    ids=lambda yn: 'license:{0}'.format({yn.lower().replace(' ', '_').replace('.', '_')}),  # noqa: Z221
)
def context_combination(
    use_pypi_deployment_with_travis,
    add_pyup_badge,
    command_line_interface,
    create_author_file,
    open_source_license,
):
    """Fixture that parametrize the function where it's used."""
    return {
        'use_pypi_deployment_with_travis': use_pypi_deployment_with_travis,
        'add_pyup_badge': add_pyup_badge,
        'command_line_interface': command_line_interface,
        'create_author_file': create_author_file,
        'open_source_license': open_source_license,
    }


def test_linting_passes(cookies, context_combination):
    """
    Generated project should pass pre-commit.

    This is parametrized for each combination from ``context_combination`` fixture
    """
    baked_result = cookies.bake(extra_context=context_combination, template=str(settings.BASE_DIR))
    project_path = str(baked_result.project)

    try:
        sh.git('init', _cwd=project_path)
        sh.git('add', '.', _cwd=project_path)
        sh.pre_commit('install', _cwd=project_path)
        sh.pre_commit('run', '--all-files', _cwd=project_path)
    except sh.ErrorReturnCode as error:
        pytest.fail(error.stdout)
