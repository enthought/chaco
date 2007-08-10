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
    version='3.0a1',
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
        "enthought.etsconfig",
        "enthought.traits",
        "enthought.kiva",
        "enthought.enable2",
    ],
    extras_require = {
        # All non-ets dependencies should be in this extra to ensure users can
        # decide whether to require them or not.
        'nonets': [
            'numpy >=1.0.2',
            ],
        },
    namespace_packages = [
        "enthought",
        ],
    packages = find_packages(
        exclude=['docs', 'examples', 'examples.zoomed_plot']
        ),
    tests_require = [
        'nose >= 0.9',
        ],
    test_suite = 'nose.collector',
    url = 'http://code.enthought.com/chaco',
    version='3.0.0a1',
    zip_safe = False,
    )
