
# Major library imports
from numpy import array, asarray, empty, sometrue, transpose, vstack, zeros

# Enthought library imports
from enthought.traits.api import Any, Array, Enum, Event, false, Instance, \
                                 Property, Trait, true
from enthought.kiva.agg import points_in_polygon

# Chaco imports
from enthought.chaco2.api import AbstractController, AbstractDataSource

class LassoSelection(AbstractController):
    """
    LassoSelection is a controller that represents the interaction of lassoing
    a set of points.
    """
    # Dataspace points is an Nx2 array of points in data space representing the
    # polygon.
    dataspace_points = Array
    
    # Fires whenever dataspace_points changes, necessitating a redraw of the
    # selection region.
    updated = Event
    
    # Fires when the selection mask changes.
    selection_changed = Event
    
    # Fires when the user lifts the mouse and finalizes the selection
    selection_completed = Event
    
    # If True, the selection mask will be updated as the mouse moves, rather
    # than only at the beginning and end of the selection operation
    incremental_select = false
    
    # Does the lasso select points of the dataset to include in the selection,
    # or exclude from selection?  This essentially inverts the selection mask.
    selection_mode = Enum("include", "exclude")
    
    # The datasource that the mask of selected points should attach to.  Note
    # that the indices in this must match the indices of the data in the plot.
    selection_datasource = Instance(AbstractDataSource)
    
    # By default plot is just self.component.  We use this to do the mapping
    # from screen space to data space
    plot = Property

    event_state = Enum('normal', 'selecting')

    #----------------------------------------------------------------------
    # Private Traits
    #----------------------------------------------------------------------
    
    _plot = Trait(None, Any)

    
    #----------------------------------------------------------------------
    # Event Handlers
    #----------------------------------------------------------------------
    
    def normal_left_down(self, event):
        # We may want to generalize this for the n-dimensional case...
        self.selection_datasource.metadata['selection'] = zeros(len(self.selection_datasource.get_data()))
        self.dataspace_points = empty((0,2))
        self.event_state = 'selecting'
        self.selecting_mouse_move(event)
        return
        
    def selecting_left_up(self, event):
        self.event_state = 'normal'
        self.selection_completed = True
        self._update_selection()
        return

    def selecting_mouse_move(self, event):
        new_point = self._map_data(array((event.x, event.y)))
        self.dataspace_points = vstack((self.dataspace_points, array((new_point,))))
        self.updated = True
        if self.incremental_select:
            self._update_selection()
        return

    def selecting_mouse_leave(self, event):
        self.selecting_left_up(event)
        return
        
    #----------------------------------------------------------------------
    # Protected Methods
    #----------------------------------------------------------------------
    
    def _dataspace_points_default(self):
        return empty((0,2))
    
    def _update_selection(self):
        if len(self.dataspace_points)>0:
            selected_mask = points_in_polygon(self._get_data(), self.dataspace_points, False)
            if sometrue(selected_mask) and self.selection_mode == "exclude":
                selected_mask = 1 - selected_mask
            if sometrue(selected_mask != self.selection_datasource.metadata['selection']):
                self.selection_datasource.metadata['selection'] = selected_mask
                self.selection_changed = True
        return
    def _map_screen(self, points):
        """
        Maps a point in data space to a point in screen space on the plot. 
        Normally a pass-through, but may do more in specialized plots.
        """
        return self.plot.map_screen(points)[:,:2]
    
    def _map_data(self, point):
        """
        Maps a point in screen space to data space.  Normally a pass-through, but
        for plots that have more data than just x,y, proper transormations need to
        happen here.
        """
        return self.plot.map_data(point, all_values=True)[:2]
    
    def _get_data(self):
        """
        Returns the datapoints in the plot, as an Nx2 array of (x,y).
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

    
