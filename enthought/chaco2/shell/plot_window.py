""" Defines the PlotWindow class.
"""
import wx
from enthought.enable2.wx_backend.api import Window
from enthought.chaco2.api import ArrayPlotData, Plot
from enthought.traits.api import Bool

class PlotWindow(wx.Frame):
    """ A window for holding top-level plot containers.
    
    Contains many utility methods for controlling the appearance of the
    window, which mostly pass through to underlying WX calls.
    """

    def __init__(self, is_image=False, *args, **kw):
        kw["size"] = (600,600)
        wx.Frame.__init__(self, None, *args, **kw )
        
        #self.image = image
        # Create an empty top-level container
        if is_image:
            top_container = self._create_top_img_container()
        else:
            top_container = self._create_top_container()

        # The PlotSession of which we are a part.  We need to know this in order
        # to notify it of our being closed, etc.
        self.session = None

        # Create the Enable Window object, and store a reference to it.
        # (This will be handy later.)  The Window requires a WX parent object
        # as its first argument, so we just pass 'self'.
        self.plot_window = Window(self, component=top_container)
        
        # We'll create a default sizer to put our plot_window in.
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # Since Window is an Enable object, we need to get its corresponding
        # WX control.  This is stored in its ".control" attribute.
        sizer.Add(self.plot_window.control, 1, wx.EXPAND)

        # Hook up event handlers for destroy, etc.
        wx.EVT_WINDOW_DESTROY(self, self._on_window_close)
        
        # More WX boilerplate.
        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        self.Show(True)
        return

    def get_container(self):
        return self.plot_window.component

    def set_container(self, container):
        self.plot_window.component = container
    
    def iconize(self, iconize):
        """Iconizes the window if *iconize* is True.
        """
        self.Iconize(iconize)
    
    def maximize(self, maximize):
        """ If *maximize* is True, maximizes the window size; restores if False.
        """
        self.Maximize(maximize)

    def set_size(self, width, height):
        self.SetSize((width, height))

    def set_title(self, title):
        self.SetTitle(title)

    def raise_window(self):
        """Raises this window to the top of the window hierarchy.
        """
        self.Raise()

    def close(self):
        self.Close()

    # This is a Python property because this is not a HasTraits subclass.
    container = property(get_container, set_container)

    #------------------------------------------------------------------------
    # Private methods
    #------------------------------------------------------------------------

    def _create_top_container(self):
        return Plot(padding = 50, fill_padding = True, bgcolor = "lightgray",
                    use_backbuffer = True)

    def _create_top_img_container(self):
        return Plot(padding = 50, fill_padding = True, bgcolor = "lightgray",
                    use_backbuffer = True, value_direction="flipped")


    def _on_window_close(self, event):
        if self.session:
            try:
                ndx = self.session.windows.index(self)
                self.session.del_window(ndx)
            except ValueError:
                pass


# EOF
