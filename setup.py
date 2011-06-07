#!/usr/bin/env python
#
# Copyright (c) 2008-2011 by Enthought, Inc.
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

* `Numpy <http://pypi.python.org/pypi/numpy>`_
* `distribute <http://pypi.python.org/pypi/distribute>`_
"""

from numpy import get_include
from setuptools import setup, Extension, find_packages


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
    'chaco.contour.contour',
    sources=['chaco/contour/cntr.c'],
    include_dirs=[get_include()],
    define_macros=[('NUMPY', None)]
    )

# Commenting this out for now, until we get the module fully tested and working
#speedups = Extension(
#    'chaco._speedups',
#    sources = ['chaco/_speedups.cpp'],
#    include_dirs = [get_include()],
#    define_macros=[('NUMPY', None)]
#    )


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
    data_files=[('chaco/layers/data',
        ['chaco/layers/data/Dialog-error.svg',
         'chaco/layers/data/Dialog-warning.svg',
         'chaco/layers/data/range_selection.svg'])],
    package_data={'chaco': ['tools/toolbars/images/*.png']},
    description = DOCLINES[1],
    download_url = ('http://www.enthought.com/repo/ets/chaco-%s.tar.gz' %
                    INFO['version']),
    ext_modules = [contour],
    html_doc_repo = 'https://svn.enthought.com/svn/cec/trunk/projects/chaco/docs/',
    include_package_data = True,
    install_requires = INFO["install_requires"],
    license = 'BSD',
    long_description = '\n'.join(DOCLINES[3:]),
    maintainer = 'ETS Developers',
    maintainer_email = 'enthought-dev@enthought.com',
    name = INFO["name"],
    packages = find_packages(exclude=[
        'docs',
        'examples',
        'examples.zoomed_plot'
        ]),
    platforms = ["Windows", "Linux", "Mac OS-X", "Unix", "Solaris"],
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
