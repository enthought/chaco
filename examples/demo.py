#-------------------------------------------------------------------------------
#
#  Copyright (c) 2009, Enthought, Inc.
#  All rights reserved.
# 
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
# 
#  Author: Vibha Srinivasan
#  Date: 02/03/2009
#  
#-------------------------------------------------------------------------------

""" Run the Chaco demo.
"""

from enthought.traits.ui.extras.demo import demo

# Uncomment the config_filename portion to see a tree editor based on the
# examples.cfg file.
demo(use_files=True, 
     # config_filename='examples.cfg'
    )
    
