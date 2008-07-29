#!/usr/bin/env python
#
# Copyright (c) 2008 by Enthought, Inc.
# All rights reserved.
#

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
"""


from distutils import log
from distutils.command.build import build as distbuild
from make_docs import HtmlBuild
from numpy import get_include
from pkg_resources import DistributionNotFound, parse_version, require, \
    VersionConflict
from setup_data import INFO
from setuptools import setup, Extension, find_packages
from setuptools.command.develop import develop
import os
import zipfile


# Pull the description values for the setup keywords from our file docstring.
DOCLINES = __doc__.split("\n")


# Register Python extensions
contour = Extension(
    'enthought.chaco.contour.contour',
    sources=['enthought/chaco/contour/cntr.c'],
    include_dirs=[get_include()],
    define_macros=[('NUMPY', None)]
    )

speedups = Extension(
    'enthought.chaco._speedups',
    sources = ['enthought/chaco/_speedups.cpp'],
    include_dirs = [get_include()],
    define_macros=[('NUMPY', None)]
    )


# Function to generate docs from source when building the project.
def generate_docs():
    """ If sphinx is installed, generate docs.
    """
    doc_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'docs')
    source_dir = os.path.join(doc_dir, 'source')
    html_zip = os.path.join(doc_dir,  'html.zip')
    dest_dir = doc_dir

    required_sphinx_version = "0.4.1"
    sphinx_installed = False
    try:
        require("Sphinx>=%s" % required_sphinx_version)
        sphinx_installed = True
    except (DistributionNotFound, VersionConflict):
        log.warn('Sphinx install of version %s could not be verified.'
            ' Trying simple import...' % required_sphinx_version)
        try:
            import sphinx
            if parse_version(sphinx.__version__) < parse_version(
                required_sphinx_version):
                log.error("Sphinx version must be >=" +\
                    "%s." % required_sphinx_version)
            else:
                sphinx_installed = True
        except ImportError:
            log.error("Sphnix install not found.")

    if sphinx_installed:
        log.info("Generating %s documentation..." % INFO['name'])
        docsrc = source_dir
        target = dest_dir

        try:
            build = HtmlBuild()
            build.start({
                'commit_message': None,
                'doc_source': docsrc,
                'preserve_temp': True,
                'subversion': False,
                'target': target,
                'verbose': True,
                'versioned': False
                }, [])
            del build

        except:
            log.error("The documentation generation failed.  Falling back to "
                "the zip file.")

            # Unzip the docs into the 'html' folder.
            unzip_html_docs(html_zip, doc_dir)
    else:
        # Unzip the docs into the 'html' folder.
        log.info("Installing %s documentaion from zip file.\n" % INFO['name'])
        unzip_html_docs(html_zip, doc_dir)

def unzip_html_docs(src_path, dest_dir):
    """ Given a path to a zipfile, extract its contents to a given 'dest_dir'.
    """
    file = zipfile.ZipFile(src_path)
    for name in file.namelist():
        cur_name = os.path.join(dest_dir, name)
        if not name.endswith('/'):
            out = open(cur_name, 'wb')
            out.write(file.read(name))
            out.flush()
            out.close()
        else:
            if not os.path.exists(cur_name):
                os.mkdir(cur_name)
    file.close()

class my_develop(develop):
    def run(self):
        develop.run(self)
        generate_docs()

class my_build(distbuild):
    def run(self):
        distbuild.run(self)
        generate_docs()


# The actual setup call.
setup(
    author = 'Peter Wang, et. al.',
    author_email = 'pwang@enthought.com',
    classifiers = [c.strip() for c in """\
        Development Status :: 4 - Beta
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
        """.splitlines()],
    cmdclass = {
        'develop': my_develop,
        'build': my_build
    },
    dependency_links = [
        'http://code.enthought.com/enstaller/eggs/source',
        ],
    description = DOCLINES[1],
    extras_require = INFO["extras_require"],
    ext_modules = [contour, speedups],
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
    tests_require = [
        'nose >= 0.10.3',
        ],
    test_suite = 'nose.collector',
    url = 'http://code.enthought.com/chaco',
    version = INFO["version"],
    zip_safe = False,
    )

