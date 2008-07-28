import os, zipfile
from setuptools import setup, Extension, find_packages
from numpy import get_include
from setuptools.command.develop import develop
from distutils.command.build import build as distbuild
from distutils import log
from pkg_resources import DistributionNotFound, parse_version, require, VersionConflict 

from setup_data import INFO
from make_docs import HtmlBuild

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

def generate_docs():
    """If sphinx is installed, generate docs.
    """
    doc_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'docs')
    source_dir = os.path.join(doc_dir, 'source')
    html_zip = os.path.join(doc_dir,  'html.zip')
    dest_dir = os.path.join(doc_dir, 'html')
    
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
            if parse_version(sphinx.__version__) < parse_version(required_sphinx_version):
                log.error("Sphinx version must be >=%s." % required_sphinx_version)
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
    """Given a path to a zipfile, extract
    its contents to a given 'dest_dir'.
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
        # Generate the documentation.
        generate_docs()

class my_build(distbuild):
    def run(self):
        distbuild.run(self)
        # Generate the documentation.
        generate_docs()

setup(
    author = 'Enthought, Inc',
    author_email = 'info@enthought.com',
    cmdclass = {
        'develop': my_develop,
        'build': my_build
    },
    dependency_links = [
        'http://code.enthought.com/enstaller/eggs/source',
        ],
    description = 'Chaco plotting toolkit',
    extras_require = INFO["extras_require"],
    ext_modules = [contour, speedups],
    include_package_data = True,
    install_requires = INFO["install_requires"],
    license = 'BSD',
    name = INFO["name"],
    namespace_packages = [
        "enthought",
        ],
    packages = find_packages(exclude=[
        'docs',
        'examples',
        'examples.zoomed_plot'
        ]),
    tests_require = [
        'nose >= 0.10.3',
        ],
    test_suite = 'nose.collector',
    url = 'http://code.enthought.com/chaco',
    version = INFO["version"],
    zip_safe = False,
    )
