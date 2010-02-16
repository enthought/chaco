from numpy import array

from enthought.traits.api import Any, List, Callable, Dict, Enum, Bool

from text_grid_overlay import TextGridOverlay

def basic_formatter(field, decimals):
    format_string = '%s: %%(%s).%df' % (field, field, decimals)
    def format(**kwargs):
        return format_string % kwargs
    return format

def datetime_formatter(field, time_format='%Y/%m/%d %H:%M:%S'):
    import datetime
    def format(**kwargs):
        dt = datetime.datetime.fromtimestamp(kwargs[field])
        return field+': '+dt.strftime(time_format)
    return format

def time_formatter(field):
    return datetime_formatter(field, time_format='%H:%M:%S')

def date_formatter(field):
    return datetime_formatter(field, time_format='%Y/%m/%d')


class SimpleInspectorOverlay(TextGridOverlay):
    # the inspector that I am listening to.  This should have a new_value
    # event and a visible trait for me to listen to.
    inspector = Any
    
    # fields to display
    field_formatters = List(List(Callable))

    # Anchor the text to the mouse?  (If False, then the text is in one of the
    # corners.)  Use the **align** trait to determine which corner.
    tooltip_mode = Bool(False)

    # The default state of the overlay is invisible (overrides PlotComponent).
    visible = True

    # Whether the overlay should auto-hide and auto-show based on the
    # tool's location, or whether it should be forced to be hidden or visible.
    visibility = Enum("auto", True, False)
    
    def _field_formatters_default(self):
        return [[basic_formatter('x', 2)], [basic_formatter('y', 2)]]

    def _inspector_changed(self, old, new):
        if old:
            old.on_trait_event(self._new_value_updated, 'new_value', remove=True)
            old.on_trait_change(self._tool_visible_changed, "visible", remove=True)
        if new:
            new.on_trait_event(self._new_value_updated, 'new_value')
            new.on_trait_change(self._tool_visible_changed, "visible") 
            self._tool_visible_changed()
    
    def _new_value_updated(self, event):
        if event is None:
            self.text_grid = array()
            if self.visibility == "auto":
                self.visibility = False
        elif self.visibility == "auto":
            self.visible = True

        if self.tooltip_mode:
            self.alternate_position = self.inspector.last_mouse_position
        #else:
        #    self.alternate_position = None
        
        d = event
        text = []
        self.text_grid.string_array = array([[formatter(**d) for formatter in row]
            for row in self.field_formatters])

        self.text_grid.request_redraw()

    def _visible_changed(self):
        if self.component:
            self.request_redraw()

    def _tool_visible_changed(self):
        self.visibility = self.inspector.visible
        if self.visibility != "auto":
            self.visible = self.visibility
            
            