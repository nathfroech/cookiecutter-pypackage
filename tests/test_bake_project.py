import pathlib
from contextlib import contextmanager
import shlex
import os
import sys
import subprocess
from typing import Tuple

import pytest
import sh
import yaml
import datetime
from cookiecutter.utils import rmtree
from hamcrest import assert_that, equal_to, has_key, is_, is_in, none, not_

from click.testing import CliRunner
from pytest_cases import pytest_fixture_plus

import settings

if sys.version_info > (3, 0):
    import importlib
else:
    import imp


@contextmanager
def inside_dir(dirpath):
    """
    Execute code from inside the given directory
    :param dirpath: String, path of the directory the command is being run.
    """
    old_path = os.getcwd()
    try:
        os.chdir(dirpath)
        yield
    finally:
        os.chdir(old_path)


@contextmanager
def bake_in_temp_dir(cookies, *args, **kwargs):
    """
    Delete the temporal directory that is created when executing the tests
    :param cookies: pytest_cookies.Cookies,
        cookie to be baked and its temporal files will be removed
    """
    result = cookies.bake(*args, **kwargs)
    try:
        yield result
    finally:
        rmtree(str(result.project))


def run_inside_dir(command, dirpath):
    """
    Run a command from inside a given directory, returning the exit status
    :param command: Command that will be executed
    :param dirpath: String, path of the directory the command is being run.
    """
    with inside_dir(dirpath):
        return subprocess.check_call(shlex.split(command))


def check_output_inside_dir(command, dirpath):
    "Run a command from inside a given directory, returning the command output"
    with inside_dir(dirpath):
        return subprocess.check_output(shlex.split(command))


def test_year_compute_in_license_file(cookies):
    with bake_in_temp_dir(cookies) as result:
        license_file_path = pathlib.Path(result.project) / 'LICENSE'
        now = datetime.datetime.now()
        assert_that(str(now.year), is_in(license_file_path.read_text()))


def project_info(result) -> Tuple[pathlib.Path, str, pathlib.Path]:
    """Get toplevel dir, project_slug, and project dir from baked cookies"""
    project_path = pathlib.Path(result.project)
    project_slug = project_path.name
    project_dir = project_path / project_slug
    return project_path, project_slug, project_dir


def test_bake_with_defaults(cookies):
    with bake_in_temp_dir(cookies) as result:
        project_path = pathlib.Path(result.project)
        assert_that(project_path.is_dir())
        assert_that(result.exit_code, is_(equal_to(0)))
        assert_that(result.exception, is_(none()))

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
    with bake_in_temp_dir(cookies, extra_context={'full_name': name}) as result:
        project_path = pathlib.Path(result.project)
        assert_that(project_path.is_dir())
        test_file_path = project_path / 'tests' / 'test_python_boilerplate.py'
        assert_that(test_file_path.is_file())
        tests_exit_code = run_inside_dir('make test', str(project_path))
        assert_that(tests_exit_code, is_(equal_to(0)))


# def test_bake_and_run_travis_pypi_setup(cookies):
#     # given:
#     with bake_in_temp_dir(cookies) as result:
#         project_path = str(result.project)
#
#         # when:
#         travis_setup_cmd = ('python travis_pypi_setup.py'
#                             ' --repo audreyr/cookiecutter-pypackage --password invalidpass')
#         run_inside_dir(travis_setup_cmd, project_path)
#         # then:
#         result_travis_config = yaml.load(result.project.join(".travis.yml").open())
#         min_size_of_encrypted_password = 50
#         assert len(result_travis_config["deploy"]["password"]["secure"]) > min_size_of_encrypted_password


def test_bake_without_travis_pypi_setup(cookies):
    with bake_in_temp_dir(cookies, extra_context={'use_pypi_deployment_with_travis': 'n'}) as result:
        project_path = pathlib.Path(result.project)
        result_travis_config = yaml.load(project_path.joinpath(".travis.yml").open(), yaml.FullLoader)
        assert_that(result_travis_config, not_(has_key('deploy')))
        assert_that(result_travis_config['language'], is_(equal_to('python')))


def test_bake_without_author_file(cookies):
    with bake_in_temp_dir(cookies, extra_context={'create_author_file': 'n'}) as result:
        project_path = pathlib.Path(result.project)

        assert_that(not project_path.joinpath('AUTHORS.rst').exists())
        assert_that(not project_path.joinpath('docs', 'authors.rst').exists())

        # Assert there are no spaces in the toc tree
        docs_index_path = project_path / 'docs' / 'index.rst'
        assert_that('contributing\n   history', is_in(docs_index_path.read_text()))

        # Check that
        manifest_path = project_path / 'MANIFEST.in'
        assert_that('AUTHORS.rst', not_(is_in(manifest_path.read_text())))


def test_make_help(cookies):
    with bake_in_temp_dir(cookies) as result:
        output = check_output_inside_dir('make help', str(result.project))
        assert_that(b"check code coverage quickly with the default Python", is_in(output))


@pytest.mark.parametrize('license_name,target_string', [
    pytest.param('MIT license', 'MIT ', id='mit'),
    pytest.param('BSD license', 'Redistributions of source code must retain the above copyright notice, this',
                 id='bsd'),
    pytest.param('ISC license', 'ISC License', id='isc'),
    pytest.param('Apache Software License 2.0', 'Licensed under the Apache License, Version 2.0', id='apache'),
    pytest.param('GNU General Public License v3', 'GNU GENERAL PUBLIC LICENSE', id='gnu'),
])
def test_bake_selecting_license(license_name, target_string, cookies):
    with bake_in_temp_dir(cookies, extra_context={'open_source_license': license_name}) as result:
        project_path = pathlib.Path(result.project)
        assert_that(target_string, is_in(project_path.joinpath('LICENSE').read_text()))
        assert_that(license_name, is_in(project_path.joinpath('setup.py').read_text()))


def test_bake_not_open_source(cookies):
    with bake_in_temp_dir(cookies, extra_context={'open_source_license': 'Not open source'}) as result:
        project_path = pathlib.Path(result.project)
        assert_that(project_path.joinpath('setup.py').is_file())
        assert_that(not project_path.joinpath('LICENSE').exists())
        assert_that('License', not_(is_in(project_path.joinpath('README.rst').read_text())))


# def test_project_with_hyphen_in_module_name(cookies):
#     result = cookies.bake(extra_context={'project_name': 'something-with-a-dash'})
#     assert result.project is not None
#     project_path = str(result.project)
#
#     # when:
#     travis_setup_cmd = ('python travis_pypi_setup.py'
#                         ' --repo audreyr/cookiecutter-pypackage --password invalidpass')
#     run_inside_dir(travis_setup_cmd, project_path)
#
#     # then:
#     result_travis_config = yaml.load(open(os.path.join(project_path, ".travis.yml")))
#     assert "secure" in result_travis_config["deploy"]["password"],\
#         "missing password config in .travis.yml"


def test_bake_with_no_console_script(cookies):
    context = {'command_line_interface': "No command-line interface"}
    result = cookies.bake(extra_context=context)
    project_path, project_slug, project_dir = project_info(result)
    assert_that(not project_dir.joinpath('cli.py').exists())

    setup_path = project_path / 'setup.py'
    assert_that('entry_points', not_(is_in(setup_path.read_text())))


def test_bake_with_console_script_files(cookies):
    context = {'command_line_interface': 'click'}
    result = cookies.bake(extra_context=context)
    project_path, project_slug, project_dir = project_info(result)
    assert_that(project_dir.joinpath('cli.py').is_file())

    setup_path = project_path / 'setup.py'
    assert_that('entry_points', is_in(setup_path.read_text()))


def test_bake_with_console_script_cli(cookies):
    context = {'command_line_interface': 'click'}
    result = cookies.bake(extra_context=context)
    project_path, project_slug, project_dir = project_info(result)
    module_path = str(project_dir / 'cli.py')
    module_name = '{}.{}'.format(project_slug, 'cli')
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
LICENSE_CHOICES = ['MIT license', 'BSD license', 'ISC license', 'Apache Software License 2.0',
                   'GNU General Public License v3', 'Not open source']


@pytest_fixture_plus
@pytest.mark.parametrize('use_pypi_deployment_with_travis', YN_CHOICES, ids=lambda yn: f'pypi_travis:{yn}')
@pytest.mark.parametrize('add_pyup_badge', YN_CHOICES, ids=lambda yn: f'pyup:{yn}')
@pytest.mark.parametrize('command_line_interface', ['Click', 'No command-line interface'],
                         ids=lambda yn: f'cli:{yn.lower()}')
@pytest.mark.parametrize('create_author_file', YN_CHOICES, ids=lambda yn: f'author:{yn}')
@pytest.mark.parametrize(
    'open_source_license',
    LICENSE_CHOICES,
    ids=lambda yn: 'license:{}'.format({yn.lower().replace(' ', '_').replace('.', '_')})
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
    result = cookies.bake(extra_context=context_combination, template=str(settings.BASE_DIR))
    project_path = str(result.project)

    try:
        sh.git('init', _cwd=project_path)
        sh.git('add', '.', _cwd=project_path)
        sh.pre_commit('install', _cwd=project_path)
        sh.pre_commit('run', '--all-files', _cwd=project_path)
    except sh.ErrorReturnCode as e:
        pytest.fail(e.stdout)
