from setuptools import setup, Extension, find_packages

from numpy import get_include

contour = Extension(
    'enthought.chaco2.contour.contour',
    sources=['enthought/chaco2/contour/cntr.c'],
    include_dirs=[get_include()],
    define_macros=[('NUMPY', None)]
)

setup(
    name = 'enthought.chaco2',
    version='2.1.0',
    description  = 'Chaco plotting toolkit',
    author       = 'Enthought, Inc',
    author_email = 'info@enthought.com',
    url          = 'http://code.enthought.com/chaco',
    license      = 'BSD',
    zip_safe     = False,
    packages = find_packages(),
    ext_modules = [contour],
    include_package_data = True,
    install_requires = [
        "numpy", 
        "enthought.traits", 
        "enthought.kiva", 
        "enthought.enable2",
    ],
    namespace_packages = [
        "enthought",
    ],
)
