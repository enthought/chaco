""" Defines the LassoSelection controller class.
"""
# Major library imports
from numpy import array, asarray, empty, sometrue, transpose, vstack, zeros

# Enthought library imports
from enthought.traits.api import Any, Array, Enum, Event, false, Instance, \
                                 Property, Trait, true
from enthought.kiva.agg import points_in_polygon

# Chaco imports
from enthought.chaco2.api import AbstractController, AbstractDataSource

class LassoSelection(AbstractController):
    """ A controller that represents the interaction of "lassoing" a set of 
    points.
    
    "Lassoing" means drawing an arbitrary selection region around the points
    by dragging the mouse along the outline of the region.
    """
    # An Nx2 array of points in data space representing the polygon.
    dataspace_points = Array
    
    # Fires whenever **dataspace_points** changes, necessitating a redraw of the
    # selection region.
    updated = Event
    
    # Fires when the selection mask changes.
    selection_changed = Event
    
    # Fires when the user release the mouse button and finalizes the selection.
    selection_completed = Event
    
    # If True, the selection mask is updated as the mouse moves, rather
    # than only at the beginning and end of the selection operation.
    incremental_select = false
    
    # The selection mode of the lasso pointer: "include" or "exclude" points
    # from the selection. The two settings essentially invert the selection mask.
    selection_mode = Enum("include", "exclude")
    
    # The data source that the mask of selected points is attached to.  Note
    # that the indices in this data source must match the indices of the data 
    # in the plot.
    selection_datasource = Instance(AbstractDataSource)
    
    # Mapping from screen space to data space. By default, it is just 
    # self.component.
    plot = Property

    # The possible event states of this selection tool (overrides 
    # enable2.Interactor).
    #
    # normal: 
    #     Nothing has been selected, and the user is not dragging the mouse.
    # selecting: 
    #     The user is dragging the mouse and is actively changing the 
    #     selection region.
    event_state = Enum('normal', 'selecting')

    #----------------------------------------------------------------------
    # Private Traits
    #----------------------------------------------------------------------
    
    # The PlotComponent associated with this tool.
    _plot = Trait(None, Any)

    
    #----------------------------------------------------------------------
    # Event Handlers
    #----------------------------------------------------------------------
    
    def normal_left_down(self, event):
        """ Handles the left mouse button being pressed while the tool is
        in the 'normal' state.
        
        Puts the tool into 'selecting' mode, and starts defining the selection.
        """
        # We may want to generalize this for the n-dimensional case...
        self.selection_datasource.metadata['selection'] = zeros(len(self.selection_datasource.get_data()))
        self.dataspace_points = empty((0,2))
        self.event_state = 'selecting'
        self.selecting_mouse_move(event)
        return
        
    def selecting_left_up(self, event):
        """ Handles the left mouse coming up in the 'selecting' state. 
        
        Completes the selection and switches to the 'normal' state.
        """
        self.event_state = 'normal'
        self.selection_completed = True
        self._update_selection()
        return

    def selecting_mouse_move(self, event):
        """ Handles the mouse moving when the tool is in the 'selecting' state.
        
        The selection is extended to the current mouse position.
        """
        new_point = self._map_data(array((event.x, event.y)))
        self.dataspace_points = vstack((self.dataspace_points, array((new_point,))))
        self.updated = True
        if self.incremental_select:
            self._update_selection()
        return

    def selecting_mouse_leave(self, event):
        """ Handles the mouse leaving the plot when the tool is in the 
        'selecting' state.
        
        Ends the selection operation.
        """
        self.selecting_left_up(event)
        return

    def normal_key_pressed(self, event):
        """ Handles the user pressing a key in the 'normal' state.
        
        If the user presses the Escape key, the tool is reset.
        """
        if event.character == "Esc":
            self._reset()
        return
    #----------------------------------------------------------------------
    # Protected Methods
    #----------------------------------------------------------------------
    
    def _dataspace_points_default(self):
        return empty((0,2))
    
    def _reset(self):
        self.event_state='normal'
        self.dataspace_points = empty((0,2))
        self._update_selection()
    
    def _update_selection(self):
        selected_mask = points_in_polygon(self._get_data(), self.dataspace_points, False)
        if sometrue(selected_mask) and self.selection_mode == "exclude":
            selected_mask = 1 - selected_mask
        if sometrue(selected_mask != self.selection_datasource.metadata['selection']):
            self.selection_datasource.metadata['selection'] = selected_mask
            self.selection_changed = True
        return
        
    def _map_screen(self, points):
        """ Maps a point in data space to a point in screen space on the plot.
        
        Normally this method is a pass-through, but it may do more in 
        specialized plots.
        """
        return self.plot.map_screen(points)[:,:2]
    
    def _map_data(self, point):
        """ Maps a point in screen space to data space.  
        
        Normally this method is a pass-through, but for plots that have more 
        data than just (x,y), proper transformations need to happen here.
        """
        return self.plot.map_data(point, all_values=True)[:2]
    
    def _get_data(self):
        """ Returns the datapoints in the plot, as an Nx2 array of (x,y).
        """
        return transpose(array((self.plot.index.get_data(), self.plot.value.get_data())))


    #------------------------------------------------------------------------
    # Property getter/setters
    #------------------------------------------------------------------------
    
    def _get_plot(self):
        if self._plot is not None:
            return self._plot
        else:
            return self.component
    
    def _set_plot(self, val):
        self._plot = val
        return

    
