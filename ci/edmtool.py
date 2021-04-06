#
#  Copyright (c) 2017, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
"""
Tasks for Test Runs
===================
This file is intended to be used with a python environment with the
click library to automate the process of setting up test environments
and running the test within them.  This improves repeatability and
reliability of tests be removing many of the variables around the
developer's particular Python environment.  Test environment setup and
package management is performed using `EDM http://docs.enthought.com/edm/`_

To use this to run you tests, you will need to install EDM and click
into your working environment.  You will also need to have git
installed to access required source code from github repositories.

You can then do::
    python edmtool.py install --runtime=... --toolkit=...
to create a test environment from the current codebase and::
    python edmtool.py test --runtime=... --toolkit=...
to run tests in that environment.  You can remove the environment with::
    python edmtool.py cleanup --runtime=... --toolkit=...

If you make changes you will either need to remove and re-install the
environment or manually update the environment using ``edm``, as
the install performs a ``python setup.py install`` rather than a ``develop``,
so changes in your code will not be automatically mirrored in the test
environment.  You can update with a command like::
    edm run --environment ... -- python setup.py install
You can run all three tasks at once with::
    python edmtool.py test_clean --runtime=... --toolkit=...
which will create, install, run tests, and then clean-up the environment.  And
you can run tests in all supported runtimes and toolkits (with cleanup)
using::
    python edmtool.py test_all

Currently supported runtime values are ``3.6``, and currently
supported toolkits are ``null``, ``pyqt``, ``pyqt5`` and ``pyside2``.  Not all
combinations of toolkits and runtimes will work, but the tasks will fail with
a clear error if that is the case. Tests can still be run via the usual means
in other environments if that suits a developer's purpose.

Changing This File
------------------
To change the packages installed during a test run, change the dependencies
variable below.  To install a package from github, or one which is not yet
available via EDM, add it to the `ci/requirements.txt` file (these will be
installed by `pip`).

Other changes to commands should be a straightforward change to the listed
commands for each task. See the EDM documentation for more information about
how to run commands within an EDM enviornment.
"""
import glob
import os
import subprocess
import sys
from shutil import rmtree, copy as copyfile
from tempfile import mkdtemp
from contextlib import contextmanager

import click

supported_combinations = {
    '3.6': {'pyside2', 'pyqt', 'pyqt5', 'null'},
}

dependencies = {
    "mock",
    "numpy",
    "pandas",
    "pyface",
    "pygments",
    "pyparsing",
    "traits",
    "traitsui",
    "cython",
    "enable",
    # Needed to install enable from source
    "swig",
}

# Dependencies we install from source for cron tests
# Order from packages with the most dependencies to one with the least
# dependencies. Packages are forced re-installed in this order.
source_dependencies = [
    "enable",
    "traitsui",
    "pyface",
    "traits",
]

github_url_fmt = "git+http://github.com/enthought/{0}.git#egg={0}"

extra_dependencies = {
    'pyside2': {'pyside2'},
    'pyqt': {'pyqt'},
    'pyqt5': {'pyqt5'},
    'null': set()
}

doc_dependencies = {
    "sphinx",
    "enthought_sphinx_theme"
}

doc_ignore = {
    "*/tests",
}

environment_vars = {
    'pyside2': {'ETS_TOOLKIT': 'qt4', 'QT_API': 'pyside2'},
    'pyqt': {'ETS_TOOLKIT': 'qt4', 'QT_API': 'pyqt'},
    'pyqt5': {'ETS_TOOLKIT': 'qt4', 'QT_API': 'pyqt5'},
    'null': {'ETS_TOOLKIT': 'null.image'},
}

ci_dependencies = {
    "flake8",
}


def normalize(name):
    return name.replace("_", "-")


@click.group(context_settings={"token_normalize_func": normalize})
def cli():
    pass


@cli.command()
@click.option('--runtime', default='3.6')
@click.option('--toolkit', default='null')
@click.option('--environment', default=None)
@click.option(
    "--source/--no-source",
    default=False,
    help="Install ETS packages from source",
)
def install(runtime, toolkit, environment, source):
    """ Install project and dependencies into a clean EDM environment.
    """
    parameters = get_parameters(runtime, toolkit, environment)
    parameters['packages'] = ' '.join(
        dependencies
        | extra_dependencies.get(toolkit, set())
        | ci_dependencies
    )

    if toolkit == "pyside2":
        additional_repositories = "--add-repository enthought/lgpl"
    else:
        additional_repositories = ""

    # edm commands to setup the development environment
    commands = [
        "edm environments create {environment} --force --version={runtime}",
        "edm install -y -e {environment} {packages} " + additional_repositories,
        ("edm run -e {environment} -- pip install -r ci/requirements.txt"
         " --no-dependencies"),
    ]

    click.echo("Creating environment '{environment}'".format(**parameters))
    execute(commands, parameters)

    if source:
        # Remove EDM ETS packages and install them from source
        cmd_fmt = (
            "edm plumbing remove-package "
            "--environment {environment} --force "
        )
        commands = [cmd_fmt + source_pkg for source_pkg in source_dependencies]
        execute(commands, parameters)
        source_pkgs = [
            github_url_fmt.format(pkg) for pkg in source_dependencies
        ]
        # Without the --no-dependencies flag such that new dependencies on
        # master are brought in.
        commands = [
            "python -m pip install --force-reinstall {pkg} ".format(pkg=pkg)
            for pkg in source_pkgs
        ]
        commands = [
            "edm run -e {environment} -- " + command for command in commands
        ]
        execute(commands, parameters)

    # Always install local source again with no dependencies
    # to mitigate risk of testing against a distributed release.
    install_local = (
        "edm run -e {environment} -- "
        "pip install --force-reinstall --no-dependencies ."
    )
    execute([install_local], parameters)

    click.echo('Done install')


@cli.command()
@click.option('--runtime', default='3.6')
@click.option('--toolkit', default='null')
@click.option('--environment', default=None)
def test(runtime, toolkit, environment):
    """ Run the test suite in a given environment with the specified toolkit.
    """
    parameters = get_parameters(runtime, toolkit, environment)
    environ = environment_vars.get(toolkit, {}).copy()

    environ['PYTHONUNBUFFERED'] = "1"
    commands = [
        "edm run -e {environment} -- python -W default -m "
        "coverage run -m unittest discover -v chaco"
    ]

    cwd = os.getcwd()

    # We run in a tempdir to avoid accidentally picking up wrong traitsui
    # code from a local dir.  We need to ensure a good .coveragerc is in
    # that directory, plus coverage has a bug that means a non-local coverage
    # file doesn't get populated correctly.
    click.echo("Running tests in '{environment}'".format(**parameters))
    with do_in_tempdir(files=['.coveragerc'], capture_files=['./.coverage*']):
        os.environ.update(environ)
        execute(commands, parameters)

    click.echo('Done test')


@cli.command()
@click.option('--runtime', default='3.6')
@click.option('--toolkit', default='null')
@click.option('--environment', default=None)
def cleanup(runtime, toolkit, environment):
    """ Remove a development environment.
    """
    parameters = get_parameters(runtime, toolkit, environment)
    commands = [
        "edm run -e {environment} -- python setup.py clean",
        "edm environments remove {environment} --purge -y",
    ]
    click.echo("Cleaning up environment '{environment}'".format(**parameters))
    execute(commands, parameters)
    click.echo('Done cleanup')


@cli.command()
@click.option('--runtime', default='3.6')
@click.option('--toolkit', default='null')
def test_clean(runtime, toolkit):
    """ Run tests in a clean environment, cleaning up afterwards
    """
    args = ['--toolkit={}'.format(toolkit),
            '--runtime={}'.format(runtime)]
    try:
        install(args=args, standalone_mode=False)
        test(args=args, standalone_mode=False)
    finally:
        cleanup(args=args, standalone_mode=False)


@cli.command()
@click.option('--runtime', default='3.6')
@click.option('--toolkit', default='null')
@click.option('--environment', default=None)
def update(runtime, toolkit, environment):
    """ Update/Reinstall package into environment.
    """
    parameters = get_parameters(runtime, toolkit, environment)
    commands = [
        "edm run -e {environment} -- python setup.py install"]
    click.echo("Re-installing in  '{environment}'".format(**parameters))
    execute(commands, parameters)
    click.echo('Done update')


@cli.command()
@click.option("--runtime", default="3.6", help="Python version to use")
@click.option("--toolkit", default="null", help="Toolkit and API to use")
@click.option("--environment", default=None, help="EDM environment to use")
def docs(runtime, toolkit, environment):
    """ Autogenerate documentation

    """
    parameters = get_parameters(runtime, toolkit, environment)
    packages = " ".join(doc_dependencies)
    ignore = " ".join(doc_ignore)
    commands = [
        "edm install -y -e {environment} " + packages,
    ]
    click.echo(
        "Installing documentation tools in  '{environment}'".format(
            **parameters
        )
    )
    execute(commands, parameters)
    click.echo("Done installing documentation tools")

    click.echo(
        "Regenerating API docs in  '{environment}'".format(**parameters)
    )
    api_path = os.path.join("docs", "source", "api")
    commands = [
        "edm run -e {environment} -- sphinx-apidoc -e -M --no-toc -o "
        + api_path
        + " chaco "
        + ignore
    ]
    execute(commands, parameters)
    click.echo("Done regenerating API docs")

    os.chdir("docs")
    command = (
        "edm run -e {environment} -- sphinx-build -b html "
        "-d build/doctrees "
        "source "
        "build/html"
    )
    click.echo(
        "Building documentation in  '{environment}'".format(**parameters)
    )
    try:
        execute([command], parameters)
    finally:
        os.chdir("..")
    click.echo("Done building documentation")


@cli.command()
def test_all():
    """ Run test_clean across all supported environment combinations.
    """
    for runtime, toolkits in supported_combinations.items():
        for toolkit in toolkits:
            args = ['--toolkit={}'.format(toolkit),
                    '--runtime={}'.format(runtime)]
            test_clean(args, standalone_mode=True)


@cli.command()
@click.option("--runtime", default="3.6", help="Python version to use")
@click.option("--toolkit", default="null", help="Toolkit and API to use")
@click.option("--environment", default=None, help="EDM environment to use")
def flake8(runtime, toolkit, environment):
    """ Run a flake8 check in a given environment.
    """
    parameters = get_parameters(runtime, toolkit, environment)
    targets = [
        "examples",
        "chaco",
        "setup.py",
        "ci/edmtool.py",
        "docs/source/conf.py"
    ]
    commands = [
        "edm run -e {environment} -- python -m flake8 " + " ".join(targets)
    ]
    execute(commands, parameters)


# ----------------------------------------------------------------------------
# Utility routines
# ----------------------------------------------------------------------------

def get_parameters(runtime, toolkit, environment):
    """Set up parameters dictionary for format() substitution
    """
    parameters = {'runtime': runtime, 'toolkit': toolkit,
                  'environment': environment}
    if toolkit not in supported_combinations[runtime]:
        msg = ("Python {runtime!r}, toolkit {toolkit!r}, "
               "not supported by test environments ({available})")
        available = ", ".join(
            repr(tk) for tk in sorted(supported_combinations[runtime])
        )
        raise RuntimeError(msg.format(available=available, **parameters))
    if environment is None:
        tmpl = 'chaco-test-{runtime}-{toolkit}'
        environment = tmpl.format(**parameters)
        parameters['environment'] = environment
    return parameters


@contextmanager
def do_in_tempdir(files=(), capture_files=()):
    """ Create a temporary directory, cleaning up after done.
    Creates the temporary directory, and changes into it.  On exit returns to
    original directory and removes temporary dir.
    Parameters
    ----------
    files : sequence of filenames
        Files to be copied across to temporary directory.
    capture_files : sequence of filenames
        Files to be copied back from temporary directory.
    """
    path = mkdtemp()
    old_path = os.getcwd()

    # send across any files we need
    for filepath in files:
        click.echo('copying file to tempdir: {}'.format(filepath))
        copyfile(filepath, path)

    os.chdir(path)
    try:
        yield path
        # retrieve any result files we want
        for pattern in capture_files:
            for filepath in glob.iglob(pattern):
                click.echo('copying file back: {}'.format(filepath))
                copyfile(filepath, old_path)
    finally:
        os.chdir(old_path)
        rmtree(path)


def execute(commands, parameters):
    for command in commands:
        print("[EXECUTING]", command.format(**parameters))
        try:
            subprocess.check_call(command.format(**parameters).split())
        except subprocess.CalledProcessError:
            sys.exit(1)


if __name__ == '__main__':
    cli()
