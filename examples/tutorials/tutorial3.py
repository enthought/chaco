"""Tutorial 3. Adding an interactor

In general, there are two things that need to happen in order to hook up a
tool or interactor.  The component needs to have the interactor added to
its list of tools (so that it can forward events to the interactor), and
the interactor also needs a reference to the component or plot that it
will be attached to.

Here we add a PanTool to the demo from tutorial 2.  All we need to do is to
create a new tool and attach it to the plot object. We add thePanTool wich
allows left-clicking and dragging to move the plot around.
"""

from chaco.tools.api import PanTool

from tutorial2 import demo

plot = demo.plot
plot.tools.append(PanTool(plot))

if __name__ == "__main__":
    demo.configure_traits()
