from setuptools import setup, Extension, find_packages
from numpy import get_include
from setup_data import INFO

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

setup(
    author = 'Enthought, Inc',
    author_email = 'info@enthought.com',
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
