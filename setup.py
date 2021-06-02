# Copyright (c) 2008-2019 by Enthought, Inc.
# All rights reserved.
import os
import re
import runpy
import subprocess

from numpy import get_include
from setuptools import setup, Extension, find_packages
from Cython.Build import cythonize

MAJOR = 5
MINOR = 1
MICRO = 0
PRERELEASE = ""
IS_RELEASED = False

# If this file is part of a Git export (for example created with "git archive",
# or downloaded from GitHub), ARCHIVE_COMMIT_HASH gives the full hash of the
# commit that was exported.
ARCHIVE_COMMIT_HASH = "$Format:%H$"

# Templates for version strings.
RELEASED_VERSION = "{major}.{minor}.{micro}{prerelease}"
UNRELEASED_VERSION = "{major}.{minor}.{micro}{prerelease}.dev{dev}"

# Paths to the autogenerated version file and the Git directory.
HERE = os.path.abspath(os.path.dirname(__file__))
VERSION_FILE = os.path.join(HERE, "chaco", "_version.py")
GIT_DIRECTORY = os.path.join(HERE, ".git")

# Template for the autogenerated version file.
VERSION_FILE_TEMPLATE = """\
# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# THIS FILE IS GENERATED FROM SETUP.PY

#: The full version of the package, including a development suffix
#: for unreleased versions of the package.
version = '{version}'

#: The full version of the package, same as 'version'
#: Kept for backward compatibility
full_version = version

#: The Git revision from which this release was made.
git_revision = '{git_revision}'

#: Flag whether this is a final release
is_released = {is_released}
"""


def read_module(module, package='chaco'):
    """ Read a simple .py file from chaco in a safe way.

    It would be simpler to import the file, but that can be problematic in an
    unknown system, so we exec the file instead and extract the variables.

    This will fail if things get too complex in the file being read, but is
    sufficient to get version and requirements information.
    """
    base_dir = os.path.dirname(__file__)
    module_name = package + '.' + module
    path = os.path.join(base_dir, package, module+'.py')
    with open(path, 'r', encoding='utf-8') as fp:
        code = compile(fp.read(), module_name, 'exec')
    context = {}
    exec(code, context)
    return context


# Return the git revision as a string
def _git_info():
    """
    Get information about the given commit from Git.

    Returns
    -------
    git_count : int
        Number of revisions from this commit to the initial commit.
    git_revision : str
        Commit hash for HEAD.

    Raises
    ------
    EnvironmentError
        If Git is not available.
    subprocess.CalledProcessError
        If Git is available, but the version command fails (most likely
        because there's no Git repository here).
    """
    def _minimal_ext_cmd(cmd):
        # construct minimal environment
        env = {}
        for k in ['SYSTEMROOT', 'PATH']:
            v = os.environ.get(k)
            if v is not None:
                env[k] = v
        # LANGUAGE is used on win32
        env['LANGUAGE'] = 'C'
        env['LANG'] = 'C'
        env['LC_ALL'] = 'C'
        out = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, env=env,
        ).communicate()[0]
        return out

    try:
        out = _minimal_ext_cmd(['git', 'describe', '--tags'])
    except OSError:
        out = ''

    git_description = out.strip().decode('ascii')
    expr = r'.*?\-(?P<count>\d+)-g(?P<hash>[a-fA-F0-9]+)'
    match = re.match(expr, git_description)
    if match is None:
        git_revision, git_count = 'Unknown', '0'
    else:
        git_revision, git_count = match.group('hash'), match.group('count')

    return git_count, git_revision


def git_version():
    """
    Construct version information from local variables and Git.

    Returns
    -------
    version : str
        Package version.
    git_revision : str
        The full commit hash for the current Git revision.

    Raises
    ------
    EnvironmentError
        If Git is not available.
    subprocess.CalledProcessError
        If Git is available, but the version command fails (most likely
        because there's no Git repository here).
    """
    git_count, git_revision = _git_info()
    version_template = RELEASED_VERSION if IS_RELEASED else UNRELEASED_VERSION
    version = version_template.format(
        major=MAJOR,
        minor=MINOR,
        micro=MICRO,
        prerelease=PRERELEASE,
        dev=git_count,
    )
    return version, git_revision


def archive_version():
    """
    Construct version information for an archive.

    Returns
    -------
    version : str
        Package version.
    git_revision : str
        The full commit hash for the current Git revision.

    Raises
    ------
    ValueError
        If this does not appear to be an archive.
    """
    if "$" in ARCHIVE_COMMIT_HASH:
        raise ValueError("This does not appear to be an archive.")

    version_template = RELEASED_VERSION if IS_RELEASED else UNRELEASED_VERSION
    version = version_template.format(
        major=MAJOR,
        minor=MINOR,
        micro=MICRO,
        prerelease=PRERELEASE,
        dev="-unknown",
    )
    return version, ARCHIVE_COMMIT_HASH


def write_version_file(version, git_revision, filename=VERSION_FILE):
    """
    Write version information to the version file.

    Overwrites any existing version file.

    Parameters
    ----------
    version : str
        Package version.
    git_revision : str
        The full commit hash for the current Git revision.
    filename : str
        Path to the version file.
    """
    with open(filename, "w", encoding="utf-8") as version_file:
        version_file.write(
            VERSION_FILE_TEMPLATE.format(
                version=version,
                git_revision=git_revision,
                is_released=IS_RELEASED,
            )
        )


def read_version_file():
    """
    Read version information from the version file, if it exists.

    Returns
    -------
    version : str
        The full version, including any development suffix.
    git_revision : str
        The full commit hash for the current Git revision.

    Raises
    ------
    EnvironmentError
        If the version file does not exist.
    """
    version_info = runpy.run_path(VERSION_FILE)
    return (version_info["version"], version_info["git_revision"])


def resolve_version():
    """
    Process version information and write a version file if necessary.

    Returns the current version information.

    Returns
    -------
    version : str
        Package version.
    git_revision : str
        The full commit hash for the current Git revision.
    """
    if os.path.isdir(GIT_DIRECTORY):
        # This is a local clone; compute version information and write
        # it to the version file, overwriting any existing information.
        version = git_version()
        print("Computed package version: {}".format(version))
        print("Writing version to version file {}.".format(VERSION_FILE))
        write_version_file(*version)
    elif "$" not in ARCHIVE_COMMIT_HASH:
        # This is a source archive.
        version = archive_version()
        print("Archive package version: {}".format(version))
        print("Writing version to version file {}.".format(VERSION_FILE))
        write_version_file(*version)
    elif os.path.isfile(VERSION_FILE):
        # This is a source distribution. Read the version information.
        print("Reading version file {}".format(VERSION_FILE))
        version = read_version_file()
        print("Package version from version file: {}".format(version))
    else:
        raise RuntimeError(
            "Unable to determine package version. No local Git clone "
            "detected, and no version file found at {}.".format(VERSION_FILE)
        )

    return version


if __name__ == "__main__":
    __version__, _ = resolve_version()
    data = read_module('__init__')
    __requires__ = data['__requires__']
    __extras_require__ = data['__extras_require__']

    numpy_include_dir = get_include()

    # Register Python extensions
    contour = Extension(
        'chaco.plots.contour.contour',
        sources=['chaco/plots/contour/cntr.c'],
        include_dirs=[numpy_include_dir],
        define_macros=[('NUMPY', None)],
    )

    cython_speedups = Extension(
        'chaco._cython_speedups',
        sources=['chaco/_cython_speedups.pyx'],
        include_dirs=[numpy_include_dir],
    )

    downsampling_lttb = Extension(
        'chaco.downsample._lttb',
        sources=['chaco/downsample/_lttb.pyx'],
        include_dirs=[numpy_include_dir],
    )

    cython_extensions = cythonize([cython_speedups, downsampling_lttb])
    extensions = [contour] + cython_extensions

    setup(
        name='chaco',
        version=__version__,
        author='Peter Wang, et. al.',
        author_email='info@enthought.com',
        maintainer='ETS Developers',
        maintainer_email='enthought-dev@enthought.com',
        url='http://docs.enthought.com/chaco',
        download_url='https://github.com/enthought/chaco',
        classifiers=[c.strip() for c in """\
            Development Status :: 5 - Production/Stable
            Intended Audience :: Developers
            Intended Audience :: Science/Research
            License :: OSI Approved :: BSD License
            Operating System :: MacOS
            Operating System :: Microsoft :: Windows
            Operating System :: OS Independent
            Operating System :: POSIX
            Operating System :: Unix
            Programming Language :: C
            Programming Language :: Python
            Topic :: Scientific/Engineering
            Topic :: Software Development
            Topic :: Software Development :: Libraries
            """.splitlines() if len(c.strip()) > 0],
        entry_points={
            "etsdemo_data": [
                "chaco_examples = chaco.examples._etsdemo_info:info",
            'chaco.examples': ['demo/*', 'demo/*/*'],
            ]
        },
        package_data={
            'chaco': [
                'overlays/layers/data/*.svg',
                'tests/data/PngSuite/*.png',
                'tools/toolbars/images/*.png',
            ]
        },
        description='interactive 2-dimensional plotting',
        long_description=open('README.rst').read(),
        ext_modules=extensions,
        include_package_data=True,
        install_requires=__requires__,
        extras_require=__extras_require__,
        license='BSD',
        packages=find_packages(),
        platforms=["Windows", "Linux", "Mac OS-X", "Unix", "Solaris"],
        zip_safe=False,
    )
