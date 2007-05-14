#!/usr/bin/env python

import os

def configuration(parent_package='enthought',top_path=None):
    from numpy.distutils.misc_util import Configuration
    config = Configuration('chaco2',parent_package,top_path)

    #add the parent __init__.py to allow for importing
    config.add_data_files(('..', os.path.abspath(os.path.join('..','__init__.py'))))
    
    config.add_subpackage('contour')
    config.add_data_files('doc/*.txt', 'doc/*.doc')
    config.add_subpackage('examples')
    config.add_subpackage('examples/basic')
    config.add_subpackage('examples/tutorials')
    config.add_subpackage('examples/updating_plot')
    config.add_subpackage('examples/zoomed_plot')
    
    config.add_data_dir('tests')
    config.add_data_dir('tools')
    config.add_data_dir('ui')
    config.add_data_dir('shell')
    config.add_data_dir('examples/basic')
    config.add_data_files('*.txt','LICENSE',
                          'tests/*.plt','tests/*.pss')

    return config

if __name__ == "__main__":
    try:
        from numpy.distutils.core import setup
    except ImportError:
        execfile('setup_chaco.py')
    else:
        setup(version='2.1.0',
           description  = 'Chaco plotting toolkit',
           author       = 'Enthought, Inc',
           author_email = 'info@enthought.com',
           url          = 'http://code.enthought.com/chaco',
           license      = 'BSD',
           zip_safe     = False,
           install_requires = ["enthought.traits", "enthought.kiva", "enthought.enable2"],
           configuration=configuration)
