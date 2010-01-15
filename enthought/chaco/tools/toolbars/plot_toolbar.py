import numpy
import sys

from enthought.chaco.abstract_overlay import AbstractOverlay
from enthought.chaco.tools.toolbars.toolbar_buttons import ToolbarButton, \
        IndexAxisLogButton, ValueAxisLogButton, SaveAsButton, \
        CopyToClipboardButton, ZoomResetButton
from enthought.enable.api import Container
from enthought.enable.tools.api import HoverTool
from enthought.traits.api import Bool, Float, Property, on_trait_change, List, \
        Tuple, Type, Enum

class PlotToolbarHover(HoverTool):
    _last_xy = Tuple()
    
    def _is_in(self, x, y):
        return self.component.is_in(x, y)
    
    def normal_mouse_move(self, event):
        self._last_xy = (event.x, event.y)
        super(PlotToolbarHover, self).normal_mouse_move(event)
    

    def on_hover(self):
        """ This gets called when all the conditions of the hover action have
        been met, and the tool determines that the mouse is, in fact, hovering
        over a target region on the component.

        By default, this method call self.callback (if one is configured).
        """
        for component in self.component.components:
            if component.is_in(*self._last_xy):
                self.callback(component.label)   
                return
        
        self.callback('')           


class PlotToolbar(Container, AbstractOverlay):
    """ A toolbar for embedding buttons in
    """

    buttons = List(Type(ToolbarButton))
    
    # Should the toolbar be hidden
    hiding = Bool(True)
    
    # should the toolbar go automatically go back into hiding when the mouse
    # is not hovering over it
    auto_hide = Bool(True)
    
    # the radius used to determine how round to make the toolbar's edges
    end_radius = Float(4.0)
    
    # button spacing is defined as the number of pixels on either side of
    # a button. The gap between 2 buttons will be 2 x the button spacing
    button_spacing = Float(5.0)
    
    # how many pixels to put before and after the set of buttons
    horizontal_padding = Float(5.0)

    # how many pixels to put on top and bottom the set of buttons 
    vertical_padding = Float(5.0)
    
    # The edge against which the toolbar is placed.
    location = Enum('top', 'right', 'bottom', 'left')
    
    # Should tooltips be shown?
    show_tooltips = Bool(False)

    ############################################################
    # PlotToolbar API
    ############################################################
    
    def __init__(self, component=None, *args, **kw):
        super(PlotToolbar, self).__init__(*args, **kw)
        self.component = component
        
        if component is not None and hasattr(component,'toolbar_location'):
            self.location = component.toolbar_location

        for buttontype in self.buttons:
            self.add_button(buttontype())
            
        hover_tool = PlotToolbarHover(component=self, callback=self.on_hover)
        self.tools.append(hover_tool)

        if self.location in ['top', 'bottom']:           
            self._calculate_width()
        else:
            self._calculate_height()

    
    def _buttons_default(self):
        return [ IndexAxisLogButton, ValueAxisLogButton,
                 SaveAsButton, CopyToClipboardButton, ZoomResetButton ]
    
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
        self.on_hover('')
        if self.hiding:
            self.hiding = False
            
    def on_hover(self, tooltip):
        if self.show_tooltips:
            self.component.window.set_tooltip(tooltip)
            
    def normal_left_down(self, event):
        """ handler for a left mouse click
        """
        if self.hiding:
            return
        else:
            for button in self.components:
                if button.is_in(event.x, event.y):
                    button.perform(event)
                    event.handled = True
                    break
        
    ############################################################
    # AbstractOverlay API
    ############################################################
    
    def overlay(self, other_component, gc, view_bounds=None, mode="normal"):
        """ Draws this component overlaid on another component.
        """

        starting_color = numpy.array([0.0, 1.0, 1.0, 1.0, 0.5])
        ending_color = numpy.array([1.0, 0.0, 0.0, 0.0, 0.5])
        
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

        if self.location in ['top','bottom']:
            gc.linear_gradient(x, y, x, y+100,
                    numpy.array([starting_color, ending_color]),
                    "")
        else:
            gc.linear_gradient(x, y, x+100, y,
                    numpy.array([starting_color, ending_color]),
                    "")

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

        if self.location in ['top', 'bottom']:
            if self.hiding:
                self.height = height = 10
            else:
                tallest_button = max([button.height for button in self.components])
                self.height = height = tallest_button + self.vertical_padding*2
        else:
            if self.hiding:
                self.width = width = 10
            else:
                widest_button = max([button.width for button in self.components])
                self.width = width = widest_button + self.horizontal_padding*2

        if component is not None:
            if self.location is 'top':
                self.x = (component.width - self.width)/2 + component.padding_left
                self.y = component.height + component.padding_bottom - height - 2
            elif self.location is 'bottom':
                self.x = (component.width - self.width)/2 + component.padding_left
                self.y = component.padding_bottom + 2
            elif self.location is 'left':
                self.x = component.padding_left + 2
                self.y = (component.height - self.height)/2 + component.padding_bottom
            else:  # 'right'
                self.x = component.width + component.padding_left - width - 2
                self.y = (component.height - self.height)/2 + component.padding_bottom

        if self.location in ['top', 'bottom']:
            v_position = self.y + self.vertical_padding*2

            last_button_position = self.x + self.horizontal_padding + self.button_spacing
            for button in self.components:
                button.x = last_button_position
                button.y = v_position
                last_button_position += button.width + self.button_spacing*2
        else:
            # location is 'left' or 'right'
            h_position = self.x + self.horizontal_padding

            last_button_position = self.y + self.vertical_padding + self.button_spacing
            for button in reversed(self.components):
                button.y = last_button_position
                button.x = h_position
                last_button_position += button.height + self.button_spacing*2            


    def _dispatch_stateful_event(self, event, suffix):
        if self.is_in(event.x, event.y):
            if suffix == 'mouse_move':
                self.normal_mouse_move(event)
            elif suffix == 'left_down':
                self.normal_left_down(event)
                event.handled = True
        else:
            if self.auto_hide:
                self.hiding = True
                
        return

    ############################################################
    # Trait handlers
    ############################################################

    @on_trait_change('components, location')
    def _calculate_width(self):
        if self.location in ['top', 'bottom']:
            width = self.horizontal_padding*2
            for button in self.components:
                width += button.width + self.button_spacing*2

            self.width = max(10, width)
            self._layout_needed = True
            self.request_redraw()

    @on_trait_change('components, location')
    def _calculate_height(self):
        if self.location in ['left', 'right']:
            height = self.vertical_padding*2
            for button in self.components:
                height += button.height + self.button_spacing*2

            self.height = max(10, height)
            self._layout_needed = True
            self.request_redraw()

    @on_trait_change('hiding')
    def _hiding_changed(self):
        self._layout_needed = True
        self.request_redraw()
        
    @on_trait_change('auto_hide')
    def _auto_hide_changed(self):
        self.hiding = self.auto_hide
        self.request_redraw()
