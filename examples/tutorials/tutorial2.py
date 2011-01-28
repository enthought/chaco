#!/usr/bin/env python
#
#
# Tutorial 2. Creating a plot in window.


# First we will import wx and write a little boilerplate main() function
# that runs the wx main event loop.  Note that we're using "PlotFrame"
# as the top-level frame for our application.  We'll actually define it
# later.
import wx
def main():
    app = wx.PySimpleApp()
    frame = PlotFrame(None)
    app.MainLoop()


# We'll use the plot we created in Tutorial 1...
from tutorial1 import myplot


# Now we'll define a wx Frame subclass and place our plot inside it.  Most of
# this code should be pretty familiar if you've dabbled with WX before.  The
# only new thing is that we're going to import a Window from the Enable
# library, and embed our plot in that.  This Window object just allows our
# plot to look like a generic Panel to WX.
from enthought.enable.wx_backend.api import Window
class PlotFrame(wx.Frame):
    def __init__(self, *args, **kw):
        kw["size"] = (600,600)
        wx.Frame.__init__( *(self,) + args, **kw )

        # Create the Enable Window object, and store a reference to it.
        # (This will be handy later.)  The Window requires a WX parent object
        # as its first argument, so we just pass 'self'.
        self.plot_window = Window(self, component=myplot)

        # We'll create a default sizer to put our plot_window in.
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Since Window is an Enable object, we need to get its corresponding
        # WX control.  This is stored in its ".control" attribute.
        sizer.Add(self.plot_window.control, 1, wx.EXPAND)

        # More WX boilerplate.
        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        self.Show(True)
        return

if __name__ == "__main__":
    main()
