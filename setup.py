# Copyright (c) 2008-2014 by Enthought, Inc.
# All rights reserved.
from os.path import join
from numpy import get_include
from setuptools import setup, Extension, find_packages


info = {}
execfile(join('chaco', '__init__.py'), info)

numpy_include_dir = get_include()


# Register Python extensions
contour = Extension(
    'chaco.contour.contour',
    sources=['chaco/contour/cntr.c'],
    include_dirs=[numpy_include_dir],
    define_macros=[('NUMPY', None)]
    )

cython_speedups = Extension(
    'chaco._cython_speedups',
    sources=['chaco/_cython_speedups.c'],
    include_dirs=[numpy_include_dir],
    )

# Commenting this out for now, until we get the module fully tested and working
#speedups = Extension(
#    'chaco._speedups',
#    sources = ['chaco/_speedups.cpp'],
#    include_dirs = [get_include()],
#    define_macros=[('NUMPY', None)]
#    )


setup(
    name = 'chaco',
    version = info['__version__'],
    author = 'Peter Wang, et. al.',
    author_email = 'pwang@enthought.com',
    maintainer = 'ETS Developers',
    maintainer_email = 'enthought-dev@enthought.com',
    url = 'http://code.enthought.com/projects/chaco',
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
    package_data={'chaco': ['tools/toolbars/images/*.png',
                            'layers/data/*.svg']},
    description = 'interactive 2-dimensional plotting',
    long_description = open('README.rst').read(),
    download_url = ('http://www.enthought.com/repo/ets/chaco-%s.tar.gz' %
                    info['__version__']),
    ext_modules = [contour, cython_speedups],
    include_package_data = True,
    install_requires = info['__requires__'],
    license = 'BSD',
    packages = find_packages(),
    platforms = ["Windows", "Linux", "Mac OS-X", "Unix", "Solaris"],
    zip_safe = False,
)
