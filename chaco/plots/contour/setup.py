# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

def configuration(parent_package="", top_path=None):
    from numpy.distutils.misc_util import Configuration

    config = Configuration("contour", parent_package, top_path)

    numerix_info = config.get_info("numerix")

    config.add_extension("contour", ["*.c"], **numerix_info)
    config.add_data_dir("tests")

    return config


if __name__ == "__main__":
    from numpy.distutils.core import setup

    setup(zip_safe=False, configuration=configuration)
