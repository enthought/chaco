from enthought.enable.tools.toolbars.viewport_toolbar import HoverToolbar, ViewportToolbar
from enthought.chaco.plot import Plot
from enthought.traits.api import Instance, List, Type
from enthought.traits.ui.wx.constants import WindowColor

from toolbar_buttons import ToolbarButton, IndexAxisLogButton, GhostButton, \
        CopyToClipboardButton, SaveAsButton, ZoomResetButton, \
        ValueAxisLogButton


class PlotToolbar(HoverToolbar):
    
    component = Instance(Plot)
    toolbar_height = 40
    buttons = List(Type(ToolbarButton))
    button_vposition = 0
    
    bgcolor = ( WindowColor.Red() / 255.0, WindowColor.Green() / 255.0, 
                WindowColor.Blue() / 255.0, 0.75 )
    
    #def __init__(self, component=None, *args, **kw):
        ## self.component should be a CanvasViewport
        #self.component = component
        #for buttontype in self.buttons:
            #self.add_button(buttontype())
            
        ## skip the ViewportToolbar, but call its parent
        #super(ViewportToolbar, self).__init__(*args, **kw)

    def _buttons_default(self):
        return [ IndexAxisLogButton, ValueAxisLogButton, GhostButton,
                 SaveAsButton, CopyToClipboardButton, ZoomResetButton ]
        
    def _do_layout(self, component=None):
        """ This method is essentially the same as the parent class, but with
            2 exceptions:
             1. The buttons are centered
             2. The widths are determined by the icons, not the label
        """
        
        if component is None:
            component = self.component
        
        if component is not None:
            horizontal_padding = 10
            vertical_padding = 5
            vertical_offset = 10
            
            # find the tallest button and set the height accordingly
            tallest_button = max([comp.height for comp in self.components])
            self.height = tallest_button + 2*vertical_padding
            self.button_vposition = vertical_padding/2

            # move it down a little from the top
            self.y = component.y2 - self.toolbar_height - vertical_offset

            self.width = sum([comp.width for comp in self.components]) \
                            + len(self.components)* self.button_spacing*2 \
                            + 2*horizontal_padding
            if component.width < self.width:
                self.width = component.width
                
            self.x = (component.width - self.width)/2 + component.x
            
        if self.order == "right-to-left":
            last_button_position = self.width - self.button_spacing - horizontal_padding
            for button in self.components:
                button.x = last_button_position - button.width
                button.y = self.button_vposition
                last_button_position -= button.width + self.button_spacing*2
        else:
            last_button_position = horizontal_padding
            for button in self.components:
                button.x = self.button_spacing + last_button_position
                button.y = self.button_vposition
                last_button_position += button.width + self.button_spacing*2
