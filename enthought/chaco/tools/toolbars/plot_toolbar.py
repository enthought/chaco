import numpy

from enthought.chaco.api import AbstractOverlay
from enthought.chaco.tools.toolbars.toolbar_buttons import ToolbarButton
from enthought.enable.api import Container
from enthought.traits.api import Bool, Float, Property, on_trait_change, List, Type

class PlotToolbar(Container, AbstractOverlay):
    """ A toolbar for embedding buttons in
    """

    buttons = List(Type(ToolbarButton))
    
    # Should the toolbar be hidden
    hiding = Bool(True)
    
    # the radius used to determine how round to make the toolbar's edges
    end_radius = Float(4.0)
    
    # button spacing is defined as the number of pixels on either side of
    # a button. The gap between 2 buttons will be 2 x the button spacing
    button_spacing = Float(5.0)
    
    # how many pixels to put before and after the set of buttons 
    horizontal_padding = Float(5.0)

    # how many pixels to put on top and bottom the set of buttons 
    vertical_padding = Float(5.0)

    ############################################################
    # PlotToolbar API
    ############################################################
    
    def __init__(self, component=None, *args, **kw):
        super(PlotToolbar, self).__init__(*args, **kw)
        self.component = component
        
        for buttontype in self.buttons:
            self.add_button(buttontype())
            
        self._calculate_width()
    
    def add_button(self, button):
        """ adds a button to the toolbar
        """
        self.add(button)
        button.toolbar_overlay = self
        self._layout_needed = True
        return

    def normal_mouse_move(self, event):
        """ handler for normal mouse move
        """
        if self.hiding:
            self.hiding = False
            
    def normal_left_down(self, event):
        """ handler for a left mouse click
        """
        if self.hiding:
            return
        else:
            for button in self.components:
                if button.is_in(event.x, event.y):
                    button.perform(event)
                    break
        
    ############################################################
    # AbstractOverlay API
    ############################################################
    
    def overlay(self, other_component, gc, view_bounds=None, mode="normal"):
        """ Draws this component overlaid on another component.
        """

        starting_color = numpy.array([0.0, 1.0, 1.0, 1.0, 1.0])
        ending_color = numpy.array([1.0, 0.0, 0.0, 0.0, 1.0])
        
        x = self.x
        y = self.y
        height = self.height
        
        gc.save_state()

        gc.begin_path()
        gc.move_to(x + self.end_radius, y)
        gc.arc_to(x + self.width, y,
                x + self.width,
                y + self.end_radius, self.end_radius)
        gc.arc_to(x + self.width,
                y + height,
                x + self.width - self.end_radius,
                y + height, self.end_radius)
        gc.arc_to(x, y + height,
                x, y,
                self.end_radius)
        gc.arc_to(x, y,
                x + self.width + self.end_radius,
                y, self.end_radius)

        gc.linear_gradient(x, y, x, y+100,
                numpy.array([starting_color, ending_color]),
                2, "")

        gc.draw_path()

        if not self.hiding:
            for button in self.components:
                button.draw(gc)

        gc.restore_state()

    def is_in(self, x, y):
        if (x >= self.x and x <= self.x2) and (y >= self.y and y <= self.y2):
            return True
        return False

    def _do_layout(self, component=None):
        if component is None:
            component = self.component

        if self.hiding:
            self.height = height = 10
        else:
            tallest_button = max([button.height for button in self.components])
            self.height = height = tallest_button + self.vertical_padding*2

        if component is not None:
            self.x = (component.width - self.width)/2 + component.padding_left
            self.y = component.height + component.padding_bottom - height - 2
            

        v_position = self.y + self.vertical_padding

        last_button_position = self.x + self.horizontal_padding
        for button in self.components:
            button.x = last_button_position
            button.y = v_position
            last_button_position += button.width + self.button_spacing*2
        

    
    def _dispatch_stateful_event(self, event, suffix):
        if self.is_in(event.x, event.y):
            if suffix == 'mouse_move':
                self.normal_mouse_move(event)
            elif suffix == 'left_down':
                self.normal_left_down(event)
                event.handled = True
        else:
            self.hiding = True
                
        return

    ############################################################
    # Trait handlers
    ############################################################
    
    @on_trait_change('components')
    def _calculate_width(self):
        width = self.horizontal_padding*2
        for button in self.components:
            width += button.width + self.button_spacing*2

        self.width = max(10, width)
            
    @on_trait_change('hiding')
    def _hiding_changed(self):
        self._layout_needed = True
        self.request_redraw()
        