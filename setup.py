# Copyright (c) 2008-2015 by Enthought, Inc.
# All rights reserved.
import os
import re
import subprocess

from numpy import get_include
from setuptools import setup, Extension, find_packages

MAJOR = 4
MINOR = 7
MICRO = 0

IS_RELEASED = False

VERSION = '%d.%d.%d' % (MAJOR, MINOR, MICRO)

# Name of the directory containing the package.
PKG_PATHNAME = 'chaco'

# Name of the file containing the version information.
_VERSION_FILENAME = os.path.join(PKG_PATHNAME, '_version.py')


def read_version_py(path):
    """ Read a _version.py file in a safe way. """
    with open(path, 'r') as fp:
        code = compile(fp.read(), 'chaco._version', 'exec')
    context = {}
    exec(code, context)
    return context['git_revision'], context['full_version']


def git_version():
    """ Parse version information from the current git commit.

    Parse the output of `git describe` and return the git hash and the number
    of commits since the last version tag.
    """

    def _minimal_ext_cmd(cmd):
        # construct minimal environment
        env = {}
        for k in ['SYSTEMROOT', 'PATH', 'HOME']:
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
        # We ask git to find the latest tag matching a glob expression. The
        # intention is to find a release tag of the form '4.50.2'. Strictly
        # speaking, the glob expression also matches tags of the form
        # '4abc.5xyz.2gtluuu', but it's very difficult with glob expressions
        # to distinguish between the two cases, and the likelihood of a
        # problem is minimal.
        out = _minimal_ext_cmd(
            ['git', 'describe', '--match', '[0-9]*.[0-9]*.[0-9]*', '--tags'])
    except OSError:
        out = ''

    git_description = out.strip().decode('ascii')
    expr = r'.*?\-(?P<count>\d+)-g(?P<hash>[a-fA-F0-9]+)'
    match = re.match(expr, git_description)
    if match is None:
        git_revision, git_count = 'Unknown', '0'
    else:
        git_revision, git_count = match.group('hash'), match.group('count')

    return git_revision, git_count


def write_version_py(filename=_VERSION_FILENAME):
    """ Create a file containing the version information. """

    template = """\
# This file was automatically generated from the `setup.py` script.
version = '{version}'
full_version = '{full_version}'
git_revision = '{git_revision}'
is_released = {is_released}

if not is_released:
    version = full_version
"""
    # Adding the git rev number needs to be done inside
    # write_version_py(), otherwise the import of _version messes
    # up the build under Python 3.
    fullversion = VERSION
    chaco_version_path =  os.path.join(
        os.path.dirname(__file__), 'chaco', '_version.py')
    if os.path.exists('.git'):
        git_rev, dev_num = git_version()
    elif os.path.exists(filename):
        # must be a source distribution, use existing version file
        try:
            git_rev, fullversion = read_version_py(chaco_version_path)
        except (SyntaxError, KeyError):
            raise RuntimeError("Unable to read git_revision. Try removing "
                               "chaco/_version.py and the build directory "
                               "before building.")


        match = re.match(r'.*?\.dev(?P<dev_num>\d+)', fullversion)
        if match is None:
            dev_num = '0'
        else:
            dev_num = match.group('dev_num')
    else:
        git_rev = 'Unknown'
        dev_num = '0'

    if not IS_RELEASED:
        fullversion += '.dev{0}'.format(dev_num)

    with open(filename, "wt") as fp:
        fp.write(template.format(version=VERSION,
                                 full_version=fullversion,
                                 git_revision=git_rev,
                                 is_released=IS_RELEASED))


if __name__ == "__main__":
    write_version_py()
    from chaco import __requires__, __version__

    numpy_include_dir = get_include()

    # Register Python extensions
    contour = Extension(
        'chaco.contour.contour',
        sources=['chaco/contour/cntr.c'],
        include_dirs=[numpy_include_dir],
        define_macros=[('NUMPY', None)],
    )

    cython_speedups = Extension(
        'chaco._cython_speedups',
        sources=['chaco/_cython_speedups.c'],
        include_dirs=[numpy_include_dir],
    )

    downsampling_lttb = Extension(
        'chaco.downsample._lttb',
        sources=['chaco/downsample/_lttb.c'],
        include_dirs=[numpy_include_dir],
    )

    # Commenting this out for now, until we get the module fully tested and
    # working
    #speedups = Extension(
    #    'chaco._speedups',
    #    sources = ['chaco/_speedups.cpp'],
    #    include_dirs = [get_include()],
    #    define_macros=[('NUMPY', None)],
    #)

    setup(
        name = 'chaco',
        version = __version__,
        author = 'Peter Wang, et. al.',
        author_email = 'info@enthought.com',
        maintainer = 'ETS Developers',
        maintainer_email = 'enthought-dev@enthought.com',
        url = 'http://docs.enthought.com/chaco',
        download_url = 'https://github.com/enthought/chaco',
        classifiers = [c.strip() for c in """\
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
        package_data={
            'chaco': ['tools/toolbars/images/*.png',
                      'layers/data/*.svg',
                      'tests/data/PngSuite/*.png']
        },
        description = 'interactive 2-dimensional plotting',
        long_description = open('README.rst').read(),
        ext_modules = [contour, cython_speedups, downsampling_lttb],
        include_package_data = True,
        install_requires = __requires__,
        license = 'BSD',
        packages = find_packages(),
        platforms = ["Windows", "Linux", "Mac OS-X", "Unix", "Solaris"],
        zip_safe = False,
        use_2to3=False,
    )
