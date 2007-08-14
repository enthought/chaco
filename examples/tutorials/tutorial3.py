#!/usr/bin/env python
#
#
# Tutorial 3. Adding an interactor

# We can reuse the plot, frame, and even the mainloop from tutorial 2.  All we need
# to do is to create a new tool and attach it to the plot object.
from tutorial2 import myplot, PlotFrame, main


# The PanTool allows left-clicking and dragging to move the plot around.
from enthought.chaco2.tools.api import PanTool


# In general, there are two things that need to happen in order to hook up a
# tool or interactor.  The component needs to have the interactor added to
# its list of tools (so that it can forward events to the interactor), and
# the interactor also needs a reference to the component or plot that it
# will be attached to.
myplot.tools.append(PanTool(myplot))


# And now we just run it.
if __name__ == "__main__":
    main()
    