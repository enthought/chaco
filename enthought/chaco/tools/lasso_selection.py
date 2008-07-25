""" Defines the LassoSelection controller class.
"""
# Major library imports
import numpy
from numpy import array, empty, sometrue, transpose, vstack, zeros

# Enthought library imports
from enthought.traits.api import Any, Array, Enum, Event, Bool, Instance, \
                                 Property, Trait, List
from enthought.kiva.agg import points_in_polygon

# Chaco imports
from enthought.chaco.api import AbstractController, AbstractDataSource


class LassoSelection(AbstractController):
    """ A controller that represents the interaction of "lassoing" a set of 
    points.
    
    "Lassoing" means drawing an arbitrary selection region around the points
    by dragging the mouse along the outline of the region.
    """
    # An Nx2 array of points in data space representing all selected points.
    dataspace_points = Property(Array)
    
    # A list of all the selection polygons.
    disjoint_selections = Property(List)
    
    # Fires whenever **dataspace_points** changes, necessitating a redraw of the
    # selection region.
    updated = Event
    
    # Fires when the selection mask changes.
    selection_changed = Event
    
    # Fires when the user release the mouse button and finalizes the selection.
    selection_completed = Event
    
    # If True, the selection mask is updated as the mouse moves, rather
    # than only at the beginning and end of the selection operation.
    incremental_select = Bool(False)
    
    # The selection mode of the lasso pointer: "include", "exclude" or 
    # "invert" points from the selection. The "include" and "exclude" 
    # settings essentially invert the selection mask. The "invert" setting
    # differs from "exclude" in that "invert" inverses the selection of all 
    # points the the lasso'ed polygon, while "exclude" operates only on
    # points included in a previous selection.
    selection_mode = Enum("include", "exclude", "invert")
    
    # The data source that the mask of selected points is attached to.  Note
    # that the indices in this data source must match the indices of the data 
    # in the plot.
    selection_datasource = Instance(AbstractDataSource)
    
    # Mapping from screen space to data space. By default, it is just 
    # self.component.
    plot = Property

    # The possible event states of this selection tool (overrides 
    # enable.Interactor).
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

    # To support multiple selections, a list of cached selections and the
    # active selection are maintained. A single list is not used because the
    # active selection is re-created every time a new point is added via
    # the vstack function.
    _active_selection = Array
    _cached_selections = List(Array)
    
    #----------------------------------------------------------------------
    # Properties
    #----------------------------------------------------------------------
    
    def _get_dataspace_points(self):
        """ Returns a complete list of all selected points. 
        
            This property exists for backwards compatibility, as the 
            disjoint_selections property is almost always the preferred 
            method of accessingselected points
        """
        composite = empty((0,2))
        for region in self.disjoint_selections:
            if len(region) > 0:
                composite = vstack((composite, region))

        return composite
    
    def _get_disjoint_selections(self):
        """ Returns a list of all disjoint selections composed of 
            the previous selections and the active selection
        """
        return self._cached_selections + [self._active_selection]
    
    #----------------------------------------------------------------------
    # Event Handlers
    #----------------------------------------------------------------------
    
    def normal_left_down(self, event):
        """ Handles the left mouse button being pressed while the tool is
        in the 'normal' state.
        
        Puts the tool into 'selecting' mode, and starts defining the selection.
        """
        # We may want to generalize this for the n-dimensional case...
        
        self._active_selection = empty((0,2))

        self.selection_datasource.metadata['selection'] = zeros(len(self.selection_datasource.get_data()))
        self.selection_mode = "include"
        self.event_state = 'selecting'
        self.selecting_mouse_move(event)
        
        if (not event.shift_down) and (not event.control_down):
            self._cached_selections = []
        else:
            if event.control_down:
                self.selection_mode = "exclude"
            else:
                self.selection_mode = "include"
            
        return
        
    def selecting_left_up(self, event):
        """ Handles the left mouse coming up in the 'selecting' state. 
        
        Completes the selection and switches to the 'normal' state.
        """
        self.event_state = 'normal'
        self.selection_completed = True
        self._update_selection()
        
        self._cached_selections.append(self._active_selection)
        return

    def selecting_mouse_move(self, event):
        """ Handles the mouse moving when the tool is in the 'selecting' state.
        
        The selection is extended to the current mouse position.
        """
        new_point = self._map_data(array((event.x, event.y)))
        self._active_selection = vstack((self._active_selection, array((new_point,))))
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
        elif event.character == 'a' and event.control_down:
            self._reset()
            self._select_all()
        elif event.character == 'i' and event.control_down:
            self.selecting_left_up(None)
            self.selection_mode = 'invert'
            self._select_all()
        return
        
    #----------------------------------------------------------------------
    # Protected Methods
    #----------------------------------------------------------------------
    
    def _dataspace_points_default(self):
        return empty((0,2))
    
    def _reset(self):
        """ Resets the selection
        """
        self.event_state='normal'
        self._active_selection = empty((0,2))
        self._cached_selections = []
        self._update_selection()

    def _select_all(self):
        """ Selects all points in the plot. This is done by making a rectangle
            using the corners of the plot, which is simple but effective. A
            much cooler, but more time-intensive solution would be to make
            a selection polygon representing the convex hull.
        """
        points = [self._map_data(array((self.plot.x, self.plot.y2))),
                  self._map_data(array((self.plot.x2, self.plot.y2))),
                  self._map_data(array((self.plot.x2, self.plot.y))),
                  self._map_data(array((self.plot.x, self.plot.y)))]
                  
        self._active_selection = numpy.array(points)
        self._update_selection()
    
    
    def _update_selection(self):
        """ Sets the selection datasource's 'selection' metadata element
            to a mask of all the points selected
        """
        
        selected_mask = zeros(self.selection_datasource._data.shape, dtype=numpy.int32)
        data = self._get_data()
        
        # Compose the selection mask from the cached selections first, then
        # the active selection, taking into account the selection mode only
        # for the active selection
        
        for selection in self._cached_selections:
            selected_mask |= (points_in_polygon(data, selection, False))
            
        if self.selection_mode == 'exclude':
            selected_mask |= (points_in_polygon(data, self._active_selection, False))
            selected_mask = 1 - selected_mask
            
        elif self.selection_mode == 'invert':
            selected_mask = -1 * (selected_mask -points_in_polygon(data, self._active_selection, False))
        else:
            selected_mask |= (points_in_polygon(data, self._active_selection, False))        
            
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

    
