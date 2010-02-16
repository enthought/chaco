"""A simple inspector overlay for plots

This module provides the SimpleInspectorOverlay for displaying
information gathered from an inspector tool in a TextGrid.  By default
it is configured to work with a SimpleInspectorTool.

The module also provides some helper factory functions for creating text
formatters for dictionary values.
"""

from numpy import array

from enthought.traits.api import Any, List, Callable, Enum, Bool

from text_grid_overlay import TextGridOverlay

def basic_formatter(key, decimals):
    """Create a basic '<key>: <value>' formatting function
    
    This factory creates a function that formats a specified key and with a
    numerical value from a dictionary into a string.
    
    Parameters
    ----------
    
    key
        The dictionary key to format.
    decimals
        The number of decimal places to show.
    
    Returns
    -------
    
    format
        A factory function that takes a dictionary and returns a string.
    """
    format_string = '%s: %%(%s).%df' % (key, key, decimals)
    def format(**kwargs):
        return format_string % kwargs
    return format

def datetime_formatter(key, time_format='%Y/%m/%d %H:%M:%S'):
    """Create a datetime formatting function
    
    This factory creates a function that formats a specified key and with a
    timestamp value from a dictionary into a string.
    
    Parameters
    ----------
    
    key
        The dictionary key to format.  The corresponding value should be a
        timestamp.
    time_format
        A format string suitable for strftime().
    
    Returns
    -------
    
    format
        A factory function that takes a dictionary and returns a string.
    """
    import datetime
    def format(**kwargs):
        dt = datetime.datetime.fromtimestamp(kwargs[key])
        return key+': '+dt.strftime(time_format)
    return format

def time_formatter(key):
    """Create a time formatting function
    
    This factory creates a function that formats a specified key and with a
    timestamp value from a dictionary into a 'HH:MM:SS' format string.
    
    Parameters
    ----------
    
    key
        The dictionary key to format.  The corresponding value should be a
        timestamp.
    
    Returns
    -------
    
    format
        A factory function that takes a dictionary and returns a string.
    """
    return datetime_formatter(key, time_format='%H:%M:%S')

def date_formatter(key):
    """Create a date formatting function
    
    This factory creates a function that formats a specified key and with a
    timestamp value from a dictionary into a 'yyyy/mm/dd' format string.
    
    Parameters
    ----------
    
    key
        The dictionary key to format.  The corresponding value should be a
        timestamp.
    
    Returns
    -------
    
    format
        A factory function that takes a dictionary and returns a string.
    """
    return datetime_formatter(key, time_format='%Y/%m/%d')


class SimpleInspectorOverlay(TextGridOverlay):
    """ Simple inspector overlay for plots
    
    This is a simple overlay that listens for new_value events on a
    SimpleInspectorTool and displays formatted values in a grid.

    By default this displays the 'x' and 'y' values provided by the
    SimpleInspectorTool, but instances can provide a field_formatters
    trait which is a list of lists of callables which extract values
    from a dictionary and formats them.  Each callable corresponds to a
    cell in the underlying TextGrid component.
    
    Although by default this works with the SimpleInspectorTool, with
    appropriate field_formatters this class can be used with any inspector
    tool that follows the same API.
    """
    # XXX We should probably refactor this into a BaseInspectorOverlay
    # which handles the visibility and basic event handling, and smaller
    # version of this class which handles inserting values into a text grid
    
    # the inspector that I am listening to.  This should have a new_value
    # event and a visible trait for me to listen to.
    inspector = Any
    
    # fields to display
    field_formatters = List(List(Callable))

    # Anchor the text to the mouse?  (If False, then the text is in one of the
    # corners.)  Use the **align** trait to determine which corner.
    tooltip_mode = Bool(False)

    # The default state of the overlay is visible.
    visible = True

    # Whether the overlay should auto-hide and auto-show based on the
    # tool's location, or whether it should be forced to be hidden or visible.
    visibility = Enum("auto", True, False)
    
    #########################################################################
    # Traits Handlers
    #########################################################################
    
    def _field_formatters_default(self):
        return [[basic_formatter('x', 2)], [basic_formatter('y', 2)]]
    
    def _new_value_updated(self, event):
        if event is None:
            self.text_grid = array()
            if self.visibility == "auto":
                self.visibility = False
        elif self.visibility == "auto":
            self.visible = True

        if self.tooltip_mode:
            self.alternate_position = self.inspector.last_mouse_position
        
        d = event
        text = []
        self.text_grid.string_array = array([[formatter(**d) for formatter in row]
            for row in self.field_formatters])

        self.text_grid.request_redraw()

    def _visible_changed(self):
        if self.component:
            self.request_redraw()

    def _inspector_changed(self, old, new):
        if old:
            old.on_trait_event(self._new_value_updated, 'new_value', remove=True)
            old.on_trait_change(self._tool_visible_changed, "visible", remove=True)
        if new:
            new.on_trait_event(self._new_value_updated, 'new_value')
            new.on_trait_change(self._tool_visible_changed, "visible") 
            self._tool_visible_changed()

    def _tool_visible_changed(self):
        self.visibility = self.inspector.visible
        if self.visibility != "auto":
            self.visible = self.visibility
            
            