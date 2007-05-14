
# Major library imports
from numpy import arange, array, cumsum, hstack, isnan, ones, sum, zeros

# Enthought library imports
from enthought.traits.api import Any, Array, Either, Enum, false, Float, List, Property, \
                                 true, Trait, Tuple
from enthought.enable2.api import Container

# Local relative imports
from base_plot_container import BasePlotContainer


__all__ = ["OverlayPlotContainer", "HPlotContainer", "VPlotContainer", \
           "GridPlotContainer"]


class OverlayPlotContainer(BasePlotContainer):
    """
    A plot container that stretches all its components to fit within its
    space.  All of its components must therefore be resizable.
    """
    
    use_backbuffer = False
    
    _cached_preferred_size = Tuple

    def get_preferred_size(self, components=None):
        if self.resizable == "":
            return self.bounds
        
        if components is None:
            components = self.plot_components
        
        # this is used to determine if we should use our default bounds
        no_visible_components = True
        
        max_width = 0.0
        max_height = 0.0
        for component in components:
            if not component.visible:
                continue
            no_visible_components = False
            pref_size = None
            
            if "h" not in component.resizable:
                pref_size = component.get_preferred_size()
                if pref_size[0] > max_width:
                    max_width = pref_size[0]
            
            if "v" not in component.resizable:
                if pref_size is None:
                    pref_size = component.get_preferred_size()
                if pref_size[1] > max_height:
                    max_height = pref_size[1]

        if no_visible_components or (max_width == 0):
            max_width = self.default_size[0]
        elif "h" not in self.resizable:
            max_width = self.width
            
        if no_visible_components or (max_height == 0):
            max_height = self.default_size[1]
        elif "v" not in self.resizable:
            max_height = self.height
        
        # Add in our padding and border
        self._cached_preferred_size = (max_width, max_height)
        return self._cached_preferred_size

    def _do_layout(self):
        width, height = self.bounds
        if "h" in self.fit_components:
            width = self._cached_preferred_size[0]
        if "v" in self.fit_components:
            height = self._cached_preferred_size[1]
        
        x = self.x
        y = self.y
        width = self.width
        height = self.height
        
        for component in self.plot_components:
            if not component.visible:
                continue
            
            if "h" in component.resizable:
                component.outer_x = 0
                component.outer_width = width
            if "v" in component.resizable:
                component.outer_y = 0
                component.outer_height = height
        
        # Tell all of our components to do a layout
        for component in self.plot_components:
            component.do_layout()
        return


class StackedPlotContainer(BasePlotContainer):
    """
    Base class for 1-D stacked plot containers, horizontal and vertical.
    """
    
    # The dimension along which to stack components that are added to
    # this container.
    stack_dimension = Enum("h", "v")
    
    # The "other" dimension, i.e. the dual of the stack dimension.
    other_dimension = Enum("v", "h")
    
    # The index into obj.position and obj.bounds that corresponds to the
    # stack_dimension.  This is a class-level and not an instance-level attribute.
    # It should be 0 or 1.
    stack_index = 0
    
    def get_preferred_size(self, components=None):
        if self.resizable == "":
            return self.bounds
        
        if components is None:
            components = self.plot_components

        ndx = self.stack_index
        other_ndx = 1 - ndx
        
        no_visible_components = True
        total_size = 0
        max_other_size = 0
        for component in components:
            if not component.visible:
                continue
            
            no_visible_components = False

            pref_size = component.get_preferred_size()
            total_size += pref_size[ndx] + self.spacing
            if pref_size[other_ndx] > max_other_size:
                max_other_size = pref_size[other_ndx]
        
        if total_size >= self.spacing:
            total_size -= self.spacing
        
        if (self.stack_dimension not in self.resizable) and \
           (self.stack_dimension not in self.fit_components):
            total_size = self.bounds[ndx]
        elif no_visible_components or (total_size == 0):
            total_size = self.default_size[ndx]
        
        if (self.other_dimension not in self.resizable) and \
           (self.other_dimension not in self.fit_components):
            max_other_size = self.bounds[other_ndx]
        elif no_visible_components or (max_other_size == 0):
            max_other_size = self.default_size[other_ndx]
        
        if ndx == 0:
            self._cached_preferred_size = (total_size, max_other_size)
        else:
            self._cached_preferred_size = (max_other_size, total_size)
            
        return self._cached_preferred_size


    def _do_stack_layout(self, components, align):
        """ Helper method that does the actual work of layout """

        size = self.bounds[:]
        if self.fit_components != "":
            self.get_preferred_size()
            if "h" in self.fit_components:
                size[0] = self._cached_preferred_size[0]
            if "v" in self.fit_components:
                size[1] = self._cached_preferred_size[1]
        
        ndx = self.stack_index
        other_ndx = 1 - ndx
        other_dim = self.other_dimension

        # Compute the amount of padding used in the stack dimension and the other
        # dimension, and create new variables for the size and origin of the
        # area inside the padding.
        #~ pad_array = self.padding
        #~ total_padding = [pad_array[0]+pad_array[1], pad_array[2]+pad_array[3]]
        #~ offset_size = [size[0] - total_padding[0], size[1] - total_padding[1]]
        #~ offset_origin = [pad_array[0], pad_array[3]]  # pad_bottom is last in pad_array
        
        # Assign sizes of non-resizable components, and compute the total size
        # used by them (along the stack dimension).
        total_fixed_size = 0
        resizable_components = []
        size_prefs = {}
        total_resizable_size = 0
        
        for component in components:
            if not component.visible:
                continue
            if self.stack_dimension not in component.resizable:
                total_fixed_size += component.outer_bounds[ndx]
            else:
                preferred_size = component.get_preferred_size()
                size_prefs[component] = preferred_size
                total_resizable_size += preferred_size[ndx]
                resizable_components.append(component)
        
        # Assign sizes of all the resizable components along the stack dimension
        if resizable_components:
            space = self.spacing * (len(self.components) - 1)
            avail_size = size[ndx] - total_fixed_size - space
            if total_resizable_size > 0:
                scale = avail_size / float(total_resizable_size)
                for component in resizable_components:
                    tmp = list(component.outer_bounds)
                    tmp[ndx] = int(size_prefs[component][ndx] * scale)
                    component.outer_bounds = tmp
            else:
                each_size = int(avail_size / len(resizable_components))
                for component in resizable_components:
                    tmp = list(component.outer_bounds)
                    tmp[ndx] = each_size
                    component.outer_bounds = tmp
        
        # Loop over all the components, assigning position and computing the
        # size in the other dimension and its position.
        cur_pos = 0
        for component in components:
            if not component.visible:
                continue
            component.set_outer_position(ndx, cur_pos)
            old_outer_bounds = component.outer_bounds
            cur_pos += old_outer_bounds[ndx] + self.spacing
            
            if (old_outer_bounds[other_ndx] > size[other_ndx]) or \
                    (other_dim in component.resizable):
                # If the component is resizable in the other dimension or it exceeds the
                # container bounds, set it to the maximum size of the container
                component.set_outer_position(other_ndx, 0)
                component.set_outer_bounds(other_ndx, size[other_ndx])
            else:
                component.set_outer_position(other_ndx, 0)
                old_coord = component.outer_position[other_ndx]
                if align == "min":
                    pass
                elif align == "max":
                    component.set_outer_position(other_ndx, old_coord + size[other_ndx] - \
                                                 old_outer_bounds[other_ndx])
                elif align == "center":
                    component.set_outer_position(other_ndx, old_coord + (size[other_ndx] - \
                                                 old_outer_bounds[other_ndx]) / 2.0)
            
            component.do_layout()
        return        

    ### Persistence ###########################################################

    # PICKLE FIXME: blocked with _pickles, but not sure that was correct.
    def __getstate__(self):
        state = super(StackedPlotContainer,self).__getstate__()
        for key in ['stack_dimension', 'other_dimension', 'stack_index']:
            if state.has_key(key):
                del state[key]
        return state


class HPlotContainer(StackedPlotContainer):
    """
    Stacks all of its components horizontally.  Resizable components will share
    the free space evenly.  All components are stacked from left to right in 
    the order that they appear in the plot_components list.  valign determines
    how to float items that are not the full height of the HPlotContainer.
    """
    
    # The order in which components in the plot container are laid out
    stack_order = Enum("left_to_right", "right_to_left")

    # The amount of vertical space to put between each component
    spacing = Float(0.0)

    # The vertical alignment of objects that don't span the full height.
    valign = Enum("bottom", "top", "center")
    
    _cached_preferred_size = Tuple

    def _do_layout(self):
        if self.stack_order == "left_to_right":
            components = self.plot_components
        else:
            components = self.plot_components[::-1]
        
        if self.valign == "bottom":
            align = "min"
        elif self.valign == "center":
            align = "center"
        else:
            align = "max"
        
        return self._do_stack_layout(components, align)

    ### Persistence ###########################################################
    #_pickles = ("stack_order", "spacing")
    
    def __getstate__(self):
        state = super(HPlotContainer,self).__getstate__()
        for key in ['_cached_preferred_size']:
            if state.has_key(key):
                del state[key]
        return state



class VPlotContainer(StackedPlotContainer):
    """
    Like HPlotContainer, only stacks up plot components one on top of (or
    below) the other.  "halign" determines how to float/justify components
    that are narrower than the width of the VPlotContainer.
    """
    
    # StackedPlotContainer attributes
    stack_dimension = "v"
    other_dimension = "h"
    stack_index = 1
    
    # VPlotContainer attributes
    
    # The horizontal alignment of objects that don't span the full width.
    halign = Enum("left", "right", "center")
    
    # The order in which components in the plot container are laid out
    stack_order = Enum("bottom_to_top", "top_to_bottom")

    # The amount of horizontal space to put between each component
    spacing = Float(0.0)

    def _do_layout(self):
        if self.stack_order == "bottom_to_top":
            components = self.plot_components
        else:
            components = self.plot_components[::-1]
        if self.halign == "left":
            align = "min"
        elif self.halign == "center":
            align = "center"
        else:
            align = "max"
        
        return self._do_stack_layout(components, align)


class GridPlotContainer(BasePlotContainer):
    """ A GridContainer consists of rows and columns in a tabular format.  Each
    cell's width is the same as all other cells in its column, and each cell's
    height is the same as all other cells in its row.

    Although grid layout requires more layout information than a simple
    ordered list, we keep components as a simple list and expose a "shape"
    trait.
    """
    
    # The amount of space to put on either side of each component, expressed
    # as a tuple (h_spacing, v_spacing)
    spacing = Either(Tuple, List, Array)

    # The vertical alignment of objects that don't span the full height.
    valign = Enum("bottom", "top", "center")
    
    # The horizontal alignment of objects that don't span the full width.
    halign = Enum("left", "right", "center")

    # The shape of this container, i.e (rows, columns).  The items in self.
    # components will get shuffled around appropriately to match this
    # specification.  If there are fewer components than cells, the rest are
    # filled in with spaces.  If there are more components than cells, the
    # remainder wrap-around onto new rows as appropriate.
    shape = Trait((0,0), Either(Tuple, List, Array))

    # This property exposes the underlying grid structure of the container
    # and is the preferred way of setting and reading out its contents.
    # When read, this returns a numpy.array with dtype=object; when set,
    # nested tuples, lists, or 2D arrays can be used.
    # This is in row-major order, so that component_grid[0] is the first
    # row, and component_grid[:,0] is the first column.  The rows are ordered
    # from the top down.
    component_grid = Property

    # The internal component grid, in row-major order.  This gets updated
    # when any of the following traits change: shape, components, grid_components
    _grid = Array

    _cached_total_size = Any
    _cached_min_widths = Array
    _cached_min_heights = Array
    _cached_col_resizable = Array
    _cached_row_resizable = Array

    def get_preferred_size(self, components=None):
        if self.resizable == "":
            return self.bounds
        
        if components is None:
            components = self.component_grid
        else:
            # Convert to array; hopefully it is a list or tuple of list/tuples
            components = array(components)

        # These arrays track the maximum widths in each column and maximum
        # height in each row.
        numrows, numcols = self.shape
        min_widths = zeros(numcols)
        min_heights = zeros(numrows)
        h_resizable = ones(numcols, dtype=int)
        v_resizable = ones(numrows, dtype=int)

        no_visible_components = True
        for i, row in enumerate(components):
            for j, component in enumerate(row):
                if not component or not component.visible:
                    continue
                else:
                    no_visible_components = False

                    pref_size = component.get_preferred_size()
                    
                    min_widths[j] = max(min_widths[j], pref_size[0])
                    h_resizable[j] = h_resizable[j] & ("h" in component.resizable)
                    min_heights[i] = max(min_heights[i], pref_size[1])
                    v_resizable[i] = v_resizable[i] & ("v" in component.resizable)

        total_size = array([sum(min_widths), sum(min_heights)])

        # Account for spacing.  There are N+1 of spaces, where N is the size in
        # each dimension.
        if self.spacing is None:
            spacing = zeros(2)
        else:
            spacing = array(self.spacing)
        total_size += array(components.shape[::-1]) * spacing * 2 * (total_size>0)
        
        for orientation, ndx in (("h", 0), ("v", 1)):
            if (orientation not in self.resizable) and \
               (orientation not in self.fit_components):
                total_size[ndx] = self.bounds[ndx]
            elif no_visible_components or (total_size[ndx] == 0):
                total_size[ndx] = self.default_size[ndx]
        
        self._cached_total_size = total_size
        self._cached_min_heights = min_heights
        self._cached_min_widths = min_widths
        self._cached_col_resizable = h_resizable
        self._cached_row_resizable = v_resizable
        
        return self._cached_total_size    
    
    
    def _do_layout(self):
        if self._cached_total_size is None:
            self.get_preferred_size()
        
        size = self.bounds[:]
        if self.fit_components != "":
            self.get_preferred_size()
            if "h" in self.fit_components:
                size[0] = self._cached_total_size[0]
            if "v" in self.fit_components:
                size[1] = self._cached_total_size[1]

        # Pick out all the resizable rows and columns by checking if the
        # corresponding max height/width is 0.  This will obviously need to be
        # refactored when we improve size preference reporting (i.e. with
        # min_size and max_size).
        resiz_rows = self._cached_row_resizable
        resiz_cols = self._cached_col_resizable

        # Compute the amount of available space, and split it amongst the
        # resizable components.
        shape = array(self._grid.shape).transpose()
        if self.spacing is None:
            spacing = array([0,0])
        else:
            spacing = array(self.spacing)
        total_spacing = spacing * 2 * shape
        avail_space = array(size) - array(self._cached_total_size)
        resiz_width, resiz_height = avail_space / array([sum(resiz_cols), sum(resiz_rows)])
        if isnan(resiz_width):
            resiz_width = 0.0
        if isnan(resiz_height):
            resiz_height = 0.0

        # Set up the arrays of widths and heights
        widths = self._cached_min_widths[:]
        heights = self._cached_min_heights[:]
        widths[resiz_cols==1] = resiz_width
        heights[resiz_rows==1] = resiz_height

        # Set the baseline h and v positions for each cell.  Resizable components
        # will get these as their position, but non-resizable components will have
        # to be aligned in H and V.
        summed_widths = cumsum(hstack(([0], widths[:-1])))
        summed_heights = cumsum(hstack(([0], heights[-1:0:-1])))
        h_positions = (2*(arange(self._grid.shape[1])+1) - 1) * spacing[0] + summed_widths
        v_positions = (2*(arange(self._grid.shape[0])+1) - 1) * spacing[1] + summed_heights
        v_positions = v_positions[::-1]

        # Loop over all rows and columns, assigning position, setting bounds for
        # resizable components, and aligning non-resizable ones
        valign = self.valign
        halign = self.halign

        for j, row in enumerate(self._grid):
            for i, component in enumerate(row):
                if not component or not component.visible:
                    continue

                r = component.resizable
                x = h_positions[i]
                y = v_positions[j]
                w = widths[i]
                h = heights[j]

                if "v" not in r:
                    # Component is not vertically resizable
                    if valign == "top":
                        y += h - component.height
                    elif valign == "center":
                        y += (h - component.height) / 2
                
                if "h" not in r:
                    # Component is not horizontally resizable
                    if halign == "right":
                        x += w - component.width
                    elif halign == "center":
                        x += (w - component.width) / 2

                component.outer_position = [x,y]
                component.outer_height = h
                component.outer_width = w

                # TODO: figure out why the following causes a layout inconsistency:
                # component.outer_bounds = [w,h]

                component.do_layout()
        return

    def _reflow_layout(self):
        # Re-computes self._grid based on self.components and self.shape.
        # self.shape will be adjusted accordingly.
        numcells = self.shape[0] * self.shape[1]
        if numcells < len(self.plot_components):
            numrows, numcols = divmod(len(self.plot_components), self.shape[0])
            self.shape = (numrows, numcols)
        grid = array(self.plot_components, dtype=object)
        grid.resize(self.shape)
        grid[grid==0] = None
        self._grid = grid
        self._layout_needed = True
        return
    
    def _shape_changed(self, old, new):
        self._reflow_layout()

    def _plot_components_changed(self, old, new):
        self._reflow_layout()

    def _plot_components_items_changed(self, event):
        self._reflow_layout()

    def _get_component_grid(self):
        return self._grid

    def _set_component_grid(self, val):
        grid = array(val)
        self.set(shape=grid.shape, trait_change_notify=False)
        self._components = list(grid.flatten())
        
        # This causes _plot_components_changed() to be called
        self.plot_components = list(grid.flatten())
        return


### EOF

