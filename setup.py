import os, zipfile
from setuptools import setup, Extension, find_packages
from numpy import get_include
from setup_data import INFO

from setuptools.command.develop import develop
from distutils.command.build import build as distbuild
from distutils import log
from pkg_resources import require, DistributionNotFound
from make_docs import HtmlBuild

contour = Extension(
    'enthought.chaco2.contour.contour',
    sources=['enthought/chaco2/contour/cntr.c'],
    include_dirs=[get_include()],
    define_macros=[('NUMPY', None)]
    )

speedups = Extension(
    'enthought.chaco2._speedups',
    sources = ['enthought/chaco2/_speedups.cpp'],
    include_dirs = [get_include()],
    define_macros=[('NUMPY', None)]
    )

def generate_docs():
    """If sphinx is installed, generate docs.
    """
    doc_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)),'docs',
                           'source')
    html_zip = os.path.join(os.path.abspath(os.path.dirname(__file__)),'docs',
                            'html.zip')
    dest_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                            'docs')
    
    try:
        require("Sphinx>=0.4.1")
            
        log.info("Auto-generating documentation in %s/html" % dest_dir)
        doc_src = doc_dir
        target = dest_dir
        try:
            build = HtmlBuild()
            build.start({
                'commit_message': None,
                'doc_source': doc_src,
                'preserve_temp': True,
                'subversion': False,
                'target': target,
                'verbose': True,
                'versioned': False,
                }, [])
            del build
        except:
            log.error("The documentation generation failed."
                      " Installing from zip file.")
            
            # Unzip the docs into the 'html' folder.
            unzip_html_docs(html_zip, dest_dir)
            
    except DistributionNotFound:
        log.error("Sphinx is not installed, so the documentation could not be "
                  "generated.  Installing from zip file...")
        
        # Unzip the docs into the 'html' folder.
        unzip_html_docs(html_zip, dest_dir)

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
