#!/usr/bin/env python
#
# Copyright (c) 2008-2010 by Enthought, Inc.
# All rights reserved.

"""
Interactive 2-Dimensional Plotting

Chaco is a Python plotting application toolkit that facilitates writing
plotting applications at all levels of complexity, from simple scripts with
hard-coded data to large plotting programs with complex data interrelationships
and a multitude of interactive tools. While Chaco generates attractive static
plots for publication and presentation, it also works well for interactive data
visualization and exploration.

Features
--------
- **Flexible drawing and layout**: Plots consist of graphical components which
  can be placed inside nestable containers for layout, positioning, and event
  dispatch. Every component has a configurable rendering loop with distinct
  layers and backbuffering. Containers can draw cooperatively so that layers
  span across the containment hierarchy.
- **Modular and extensible architecture**: Chaco is object-oriented from the
  ground up for ease of extension and customization. There are clear interfaces
  and abstract classes defining extension points for writing your own custom
  behaviors, from custom tools, plot types, layouts, etc. Most classes are
  also "subclass-friendly", so that subclasses can override one or two methods
  and everything else just works.
- **Data model for ease of extension and embedding**: Chaco separates the data
  from any transformations of the data that are needed for displaying it. This
  separation makes it easier to extend Chaco, or embed it in applications.

Prerequisites
-------------
You must have the following libraries installed before building or installing
Chaco:

* `Numpy <http://pypi.python.org/pypi/numpy/1.1.1>`_ version 1.1.0 or later is
  preferred. Version 1.0.4 will work, but some tests may fail.
* `setuptools <http://pypi.python.org/pypi/setuptools/0.6c8>`_

"""

import traceback
import sys

from distutils import log
from distutils.command.build import build as distbuild
from numpy import get_include
from setuptools import setup, Extension, find_packages
from setuptools.command.develop import develop


# FIXME: This works around a setuptools bug which gets setup_data.py metadata
# from incorrect packages. Ticket #1592
#from setup_data import INFO
setup_data = dict(__name__='', __file__='setup_data.py')
execfile('setup_data.py', setup_data)
INFO = setup_data['INFO']


# Pull the description values for the setup keywords from our file docstring.
DOCLINES = __doc__.split("\n")


# Register Python extensions
contour = Extension(
    'enthought.chaco.contour.contour',
    sources=['enthought/chaco/contour/cntr.c'],
    include_dirs=[get_include()],
    define_macros=[('NUMPY', None)]
    )

# Commenting this out for now, until we get the module fully tested and working
#speedups = Extension(
#    'enthought.chaco._speedups',
#    sources = ['enthought/chaco/_speedups.cpp'],
#    include_dirs = [get_include()],
#    define_macros=[('NUMPY', None)]
#    )


class MyDevelop(develop):
    def run(self):
        develop.run(self)
        try:
            self.run_command('build_docs')
        except:
            log.warn("Couldn't build documentation:\n%s" %
                     traceback.format_exception(*sys.exc_info()))


class MyBuild(distbuild):
    def run(self):
        distbuild.run(self)
        try:
            self.run_command('build_docs')
        except:
            log.warn("Couldn't build documentation:\n%s" %
                     traceback.format_exception(*sys.exc_info()))


# The actual setup call.
setup(
    author = 'Peter Wang, et. al.',
    author_email = 'pwang@enthought.com',
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
    cmdclass = {
        'develop': MyDevelop,
        'build': MyBuild
    },
    data_files=[('enthought/chaco/layers/data',
        ['enthought/chaco/layers/data/Dialog-error.svg',
         'enthought/chaco/layers/data/Dialog-warning.svg',
         'enthought/chaco/layers/data/range_selection.svg'])],
    package_data={'enthought': ['chaco/tools/toolbars/images/*.png']},
    description = DOCLINES[1],
    download_url = ('http://www.enthought.com/repo/ETS/Chaco-%s.tar.gz' %
        INFO['version']),
    extras_require = INFO["extras_require"],
    ext_modules = [contour],
    html_doc_repo = 'https://svn.enthought.com/svn/cec/trunk/projects/chaco/docs/',
    include_package_data = True,
    install_requires = INFO["install_requires"],
    license = 'BSD',
    long_description = '\n'.join(DOCLINES[3:]),
    maintainer = 'ETS Developers',
    maintainer_email = 'enthought-dev@enthought.com',
    name = INFO["name"],
    namespace_packages = [
        "enthought",
        ],
    packages = find_packages(exclude=[
        'docs',
        'examples',
        'examples.zoomed_plot'
        ]),
    platforms = ["Windows", "Linux", "Mac OS-X", "Unix", "Solaris"],
    setup_requires = 'setupdocs>=1.0',
    ssh_server = 'code.enthought.com',
    ssh_remote_dir = '/www/htdocs/code.enthought.com/projects/chaco/',
    tests_require = [
        'nose >= 0.10.3',
        ],
    test_suite = 'nose.collector',
    url = 'http://code.enthought.com/projects/chaco',
    version = INFO["version"],
    zip_safe = False,
    )
