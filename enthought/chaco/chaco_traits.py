""" Defines various traits that are used in many places in Chaco.
"""

# Enthought library imports
from enthought.traits.api import Enum
    
#----------------------------------------------------------------------------
# Box positioning traits: used to specify positions of boxes relative to
# one another.  Generally used for layout.
#----------------------------------------------------------------------------

box_edge_enum = Enum("left", "right", "top", "bottom")

# Values correspond to: top, bottom, left, right, top left, top right, bottom 
# left, bottom right
box_position_enum = Enum("T", "B", "L", "R", "TL", "TR", "BL", "BR")

# For backwards compatibility, import LineStyle & LineStyleEditor from enable.
# (They used to be defined here.)
from enthought.enable.api import LineStyle, LineStyleEditor

# EOF
