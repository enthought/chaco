doc = \
"""
This file contains a support class that wraps up the boilerplate wx calls
that virtually all the demo programs have to use, and doesn't actually do
anything when run on its own.

Try running simple_line.py, colormapped_scatter.py, or check out any of
the programs in in tutorials/.
"""

from numpy import array
import wx

# Set up the debug logger for all chaco examples.
# We don't want users to go digging around for the default Enthought logfile
# in ~/envisage.log, so we add a handler to the global logger for a file
# "chaco.log" in the current directory.
import logging, logging.handlers
try:
    chaco_handler = logging.handlers.RotatingFileHandler("chaco.log",
                        maxBytes=1000000, backupCount=0)
    logging.getLogger().addHandler(chaco_handler)
except:
    # If we can't override the default handler, it's OK.
    pass

# This is a palette of 10 nice colors to use for mapping/discrete
# color differentiation.  From ColorBrewer.
COLOR_PALETTE = (array([166,206,227,
                        31,120,180,
                        178,223,138,
                        51,160,44,
                        251,154,153,
                        227,26,28,
                        253,191,111,
                        255,127,0,
                        202,178,214,
                        106,61,154], dtype=float)/255).reshape(10,3)


class DemoFrame(wx.Frame):
    def __init__ ( self, *args, **kw ):
        wx.Frame.__init__( *(self,) + args, **kw )
        self.SetAutoLayout( True )

        # Create the subclass's window
        self.plot_window = self._create_window()

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.plot_window.control, 1, wx.EXPAND)
        self.SetSizer(sizer)
        self.Show( True )
        return

    def _create_window(self):
        "Subclasses should override this method and return an enable.wx.Window"
        raise NotImplementedError


def demo_main(demo_class, size=(400,400), title="Chaco plot"):
    "Takes the class of the demo to run as an argument."
    app = wx.PySimpleApp()
    frame = demo_class(None, size=size, title=title)
    app.SetTopWindow(frame)
    app.MainLoop()

if __name__ == "__main__":
    print "\n" + doc + "\n"


# EOF
