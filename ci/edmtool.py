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

Currently supported runtime values are ``2.7`` and ``3.5``, and currently
supported toolkits are ``null``, ``pyqt``, and ``wx``.  Not all
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

from __future__ import print_function

import glob
import os
import subprocess
import sys
from shutil import rmtree, copy as copyfile
from tempfile import mkdtemp
from contextlib import contextmanager

import click

supported_combinations = {
    '2.7': {'pyqt', 'wx', 'null'},
    '3.5': {'pyqt', 'null'},
}

dependencies = {
    "six",
    "nose",
    "mock",
    "numpy",
    "pygments",
    "pyparsing",
    "cython"
}

extra_dependencies = {
    'pyqt': {'pyqt'},
    'wx': {'wxpython'},
    'null': set()
}

environment_vars = {
    'pyqt': {'ETS_TOOLKIT': 'qt4', 'QT_API': 'pyqt'},
    'wx': {'ETS_TOOLKIT': 'wx'},
    'null': {'ETS_TOOLKIT': 'null.image'},
}

if sys.version_info < (3, 0):
    import string
    pillow_trans = string.maketrans('<=>', '___')
else:
    pillow_trans = ''.maketrans({'<': '_', '=': '_', '>': '_'})


@click.group()
def cli():
    pass


@cli.command()
@click.option('--runtime', default='3.5')
@click.option('--toolkit', default='null')
@click.option('--pillow', default='pillow')
@click.option('--environment', default=None)
def install(runtime, toolkit, pillow, environment):
    """ Install project and dependencies into a clean EDM environment.
    """
    parameters = get_parameters(runtime, toolkit, pillow, environment)
    parameters['packages'] = ' '.join(
        dependencies | extra_dependencies.get(toolkit, set()))
    # edm commands to setup the development environment
    commands = [
        "edm environments create {environment} --force --version={runtime}",
        "edm install -y -e {environment} {packages}",
        "edm run -e {environment} -- pip install {pillow}",
        ("edm run -e {environment} -- pip install -r ci/requirements.txt"
         " --no-dependencies"),
        ("edm run -e {environment} -- "
         "pip install git+https://git@github.com/enthought/enable.git"),
        "edm run -e {environment} -- python setup.py install",
    ]
    click.echo("Creating environment '{environment}'".format(**parameters))
    execute(commands, parameters)
    click.echo('Done install')


@cli.command()
@click.option('--runtime', default='3.5')
@click.option('--toolkit', default='null')
@click.option('--pillow', default='pillow')
@click.option('--environment', default=None)
def test(runtime, toolkit, pillow, environment):
    """ Run the test suite in a given environment with the specified toolkit.
    """
    parameters = get_parameters(runtime, toolkit, pillow, environment)
    environ = environment_vars.get(toolkit, {}).copy()
    environ['PYTHONUNBUFFERED'] = "1"
    commands_nobackend = [
        "edm run -e {environment} -- coverage run -m nose.core chaco -v "
    ]

    cwd = os.getcwd()

    # We run in a tempdir to avoid accidentally picking up wrong traitsui
    # code from a local dir.  We need to ensure a good .coveragerc is in
    # that directory, plus coverage has a bug that means a non-local coverage
    # file doesn't get populated correctly.
    click.echo("Running tests in '{environment}'".format(**parameters))
    with do_in_tempdir(files=['.coveragerc'], capture_files=['./.coverage*']):
        os.environ.update(environ)
        execute(commands_nobackend, parameters)

        if toolkit != 'null':
            backend_tests = os.path.join(cwd, 'chaco/tests_with_backend')
            commands_backend = [
                ("edm run -e {{environment}} -- coverage run -a "
                 "-m nose.core -v {}").format(backend_tests)
            ]
            execute(commands_backend, parameters)

    click.echo('Done test')



@cli.command()
@click.option('--runtime', default='3.5')
@click.option('--toolkit', default='null')
@click.option('--pillow', default='pillow')
@click.option('--environment', default=None)
def cleanup(runtime, toolkit, pillow, environment):
    """ Remove a development environment.
    """
    parameters = get_parameters(runtime, toolkit, pillow, environment)
    commands = [
        "edm run -e {environment} -- python setup.py clean",
        "edm environments remove {environment} --purge -y",
    ]
    click.echo("Cleaning up environment '{environment}'".format(**parameters))
    execute(commands, parameters)
    click.echo('Done cleanup')


@cli.command()
@click.option('--runtime', default='3.5')
@click.option('--toolkit', default='null')
@click.option('--pillow', default='pillow')
def test_clean(runtime, toolkit, pillow):
    """ Run tests in a clean environment, cleaning up afterwards
    """
    args = ['--toolkit={}'.format(toolkit),
            '--runtime={}'.format(runtime),
            '--pillow={}'.format(pillow)]
    try:
        install(args=args, standalone_mode=False)
        test(args=args, standalone_mode=False)
    finally:
        cleanup(args=args, standalone_mode=False)


@cli.command()
@click.option('--runtime', default='3.5')
@click.option('--toolkit', default='null')
@click.option('--pillow', default='pillow')
@click.option('--environment', default=None)
def update(runtime, toolkit, pillow, environment):
    """ Update/Reinstall package into environment.
    """
    parameters = get_parameters(runtime, toolkit, pillow, environment)
    commands = [
        "edm run -e {environment} -- python setup.py install"]
    click.echo("Re-installing in  '{environment}'".format(**parameters))
    execute(commands, parameters)
    click.echo('Done update')


@cli.command()
def test_all():
    """ Run test_clean across all supported environment combinations.
    """
    for runtime, toolkits in supported_combinations.items():
        for toolkit in toolkits:
            args = ['--toolkit={}'.format(toolkit),
                    '--runtime={}'.format(runtime)]
            test_clean(args, standalone_mode=True)


# ----------------------------------------------------------------------------
# Utility routines
# ----------------------------------------------------------------------------

def get_parameters(runtime, toolkit, pillow, environment):
    """Set up parameters dictionary for format() substitution
    """
    parameters = {'runtime': runtime, 'toolkit': toolkit, 'pillow': pillow,
                  'environment': environment}
    if toolkit not in supported_combinations[runtime]:
        msg = ("Python {runtime}, toolkit {toolkit}, and pillow {pillow} "
               "not supported by test environments")
        raise RuntimeError(msg.format(**parameters))
    if environment is None:
        tmpl = 'chaco-test-{runtime}-{toolkit}'
        environment = tmpl.format(**parameters)
        environment += '-{}'.format(str(pillow).translate(pillow_trans))
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
