""" Defines various plot container classes, including stacked, grid, and overlay.
"""
# Major library imports
from numpy import amax, any, arange, array, cumsum, hstack, sum, zeros, zeros_like

# Enthought library imports
from traits.api import Any, Array, Either, Enum, Float, Instance, \
    List, Property, String, Trait, Tuple, Int
from enable.simple_layout import simple_container_get_preferred_size, \
                                            simple_container_do_layout
try:
    from enable.api import ConstraintsContainer
except ImportError:
    ConstraintsContainer = None

# Local relative imports
from .base_plot_container import BasePlotContainer


__all__ = ["OverlayPlotContainer", "HPlotContainer", "VPlotContainer", \
           "GridPlotContainer"]

DEFAULT_DRAWING_ORDER = ["background", "image", "underlay",      "plot",
                         "selection", "border", "annotation", "overlay"]


# Enable constraints layout is only available if kiwisolver is installed!
if ConstraintsContainer is not None:
    class ConstraintsPlotContainer(ConstraintsContainer):
        """ A Plot container that supports constraints-based layout
        """
        # !! Bits copied from BasePlotContainer !!
        container_under_layers = Tuple("background", "image", "underlay", "plot")
        draw_order = Instance(list, args=(DEFAULT_DRAWING_ORDER,))
        draw_layer = String('plot')
        # !! Bits copied from BasePlotContainer !!

    __all__.append('ConstraintsPlotContainer')


class OverlayPlotContainer(BasePlotContainer):
    """
    A plot container that stretches all its components to fit within its
    space.  All of its components must therefore be resizable.
    """

    draw_order = Instance(list, args=(DEFAULT_DRAWING_ORDER,))

    #: Do not use an off-screen backbuffer.
    use_backbuffer = False

    # Cache (width, height) of the container's preferred size.
    _cached_preferred_size = Tuple

    def get_preferred_size(self, components=None):
        """ Returns the size (width,height) that is preferred for this component.

        Overrides PlotComponent
        """
        return simple_container_get_preferred_size(self, components=components)

    def _do_layout(self):
        """ Actually performs a layout (called by do_layout()).
        """
        simple_container_do_layout(self)


class StackedPlotContainer(BasePlotContainer):
    """
    Base class for 1-D stacked plot containers, both horizontal and vertical.
    """

    draw_order = Instance(list, args=(DEFAULT_DRAWING_ORDER,))

    # The dimension along which to stack components that are added to
    # this container.
    stack_dimension = Enum("h", "v")

    # The "other" dimension, i.e., the dual of the stack dimension.
    other_dimension = Enum("v", "h")

    # The index into obj.position and obj.bounds that corresponds to
    # **stack_dimension**.  This is a class-level and not an instance-level
    # attribute. It must be 0 or 1.
    stack_index = 0

    def get_preferred_size(self, components=None):
        """ Returns the size (width,height) that is preferred for this component.

        Overrides PlotComponent.
        """
        if self.fixed_preferred_size is not None:
            self._cached_preferred_size = self.fixed_preferred_size
            return self.fixed_preferred_size

        if self.resizable == "":
            self._cached_preferred_size = self.outer_bounds[:]
            return self.outer_bounds

        if components is None:
            components = self.components

        ndx = self.stack_index
        other_ndx = 1 - ndx

        no_visible_components = True
        total_size = 0
        max_other_size = 0
        for component in components:
            if not self._should_layout(component):
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
            self._cached_preferred_size = (total_size + self.hpadding,
                                           max_other_size + self.vpadding)
        else:
            self._cached_preferred_size = (max_other_size + self.hpadding,
                                           total_size + self.vpadding)

        return self._cached_preferred_size


    def _do_stack_layout(self, components, align):
        """ Helper method that does the actual work of layout.
        """

        size = list(self.bounds)
        if self.fit_components != "":
            self.get_preferred_size()
            if "h" in self.fit_components:
                size[0] = self._cached_preferred_size[0] - self.hpadding
            if "v" in self.fit_components:
                size[1] = self._cached_preferred_size[1] - self.vpadding

        ndx = self.stack_index
        other_ndx = 1 - ndx
        other_dim = self.other_dimension

        # Assign sizes of non-resizable components, and compute the total size
        # used by them (along the stack dimension).
        total_fixed_size = 0
        resizable_components = []
        size_prefs = {}
        total_resizable_size = 0

        for component in components:
            if not self._should_layout(component):
                continue
            if self.stack_dimension not in component.resizable:
                total_fixed_size += component.outer_bounds[ndx]
            else:
                preferred_size = component.get_preferred_size()
                size_prefs[component] = preferred_size
                total_resizable_size += preferred_size[ndx]
                resizable_components.append(component)

        new_bounds_dict = {}

        # Assign sizes of all the resizable components along the stack dimension
        if resizable_components:
            space = self.spacing * (len(self.components) - 1)
            avail_size = size[ndx] - total_fixed_size - space
            if total_resizable_size > 0:
                scale = avail_size / float(total_resizable_size)
                for component in resizable_components:
                    tmp = list(component.outer_bounds)
                    tmp[ndx] = int(size_prefs[component][ndx] * scale)
                    new_bounds_dict[component] = tmp
            else:
                each_size = int(avail_size / len(resizable_components))
                for component in resizable_components:
                    tmp = list(component.outer_bounds)
                    tmp[ndx] = each_size
                    new_bounds_dict[component] = tmp

        # Loop over all the components, assigning position and computing the
        # size in the other dimension and its position.
        cur_pos = 0
        for component in components:
            if not self._should_layout(component):
                continue

            position = list(component.outer_position)
            position[ndx] = cur_pos

            bounds = new_bounds_dict.get(component, list(component.outer_bounds))
            cur_pos += bounds[ndx] + self.spacing

            if (bounds[other_ndx] > size[other_ndx]) or \
                    (other_dim in component.resizable):
                # If the component is resizable in the other dimension or it exceeds the
                # container bounds, set it to the maximum size of the container

                position[other_ndx] = 0
                bounds[other_ndx] = size[other_ndx]
            else:
                position[other_ndx] = 0
                if align == "min":
                    pass
                elif align == "max":
                    position[other_ndx] = size[other_ndx] - bounds[other_ndx]
                elif align == "center":
                    position[other_ndx] = (size[other_ndx] - bounds[other_ndx]) / 2.0

            component.outer_position = position
            component.outer_bounds = bounds
            component.do_layout()

    ### Persistence ###########################################################

    # PICKLE FIXME: blocked with _pickles, but not sure that was correct.
    def __getstate__(self):
        state = super(StackedPlotContainer,self).__getstate__()
        for key in ['stack_dimension', 'other_dimension', 'stack_index']:
            if key in state:
                del state[key]
        return state


class HPlotContainer(StackedPlotContainer):
    """
    A plot container that stacks all of its components horizontally. Resizable
    components share the free space evenly. All components are stacked from
    according to **stack_order* in the same order that they appear in the
    **components** list.
    """

    draw_order = Instance(list, args=(DEFAULT_DRAWING_ORDER,))

    #: The order in which components in the plot container are laid out.
    stack_order = Enum("left_to_right", "right_to_left")

    #: The amount of space to put between components.
    spacing = Float(0.0)

    #: The vertical alignment of objects that don't span the full height.
    valign = Enum("bottom", "top", "center")

    _cached_preferred_size = Tuple

    def _do_layout(self):
        """ Actually performs a layout (called by do_layout()).
        """
        if self.stack_order == "left_to_right":
            components = self.components
        else:
            components = self.components[::-1]

        if self.valign == "bottom":
            align = "min"
        elif self.valign == "center":
            align = "center"
        else:
            align = "max"

        return self._do_stack_layout(components, align)

    ### Persistence ###########################################################

    def __getstate__(self):
        state = super(HPlotContainer,self).__getstate__()
        for key in ['_cached_preferred_size']:
            if key in state:
                del state[key]
        return state



class VPlotContainer(StackedPlotContainer):
    """
    A plot container that stacks plot components vertically.
    """

    draw_order = Instance(list, args=(DEFAULT_DRAWING_ORDER,))

    #: Overrides StackedPlotContainer.
    stack_dimension = "v"
    #: Overrides StackedPlotContainer.
    other_dimension = "h"
    #: Overrides StackedPlotContainer.
    stack_index = 1

    # VPlotContainer attributes

    #: The horizontal alignment of objects that don't span the full width.
    halign = Enum("left", "right", "center")

    #: The order in which components in the plot container are laid out.
    stack_order = Enum("bottom_to_top", "top_to_bottom")

    #: The amount of space to put between components.
    spacing = Float(0.0)

    def _do_layout(self):
        """ Actually performs a layout (called by do_layout()).
        """
        if self.stack_order == "bottom_to_top":
            components = self.components
        else:
            components = self.components[::-1]
        if self.halign == "left":
            align = "min"
        elif self.halign == "center":
            align = "center"
        else:
            align = "max"

        return self._do_stack_layout(components, align)


class GridPlotContainer(BasePlotContainer):
    """ A GridPlotContainer consists of rows and columns in a tabular format.

    Each cell's width is the same as all other cells in its column, and each
    cell's height is the same as all other cells in its row.

    Although grid layout requires more layout information than a simple
    ordered list, this class keeps components as a simple list and exposes a
    **shape** trait.
    """

    draw_order = Instance(list, args=(DEFAULT_DRAWING_ORDER,))

    #: The amount of space to put on either side of each component, expressed
    #: as a tuple (h_spacing, v_spacing).
    spacing = Either(Tuple, List, Array)

    #: The vertical alignment of objects that don't span the full height.
    valign = Enum("bottom", "top", "center")

    #: The horizontal alignment of objects that don't span the full width.
    halign = Enum("left", "right", "center")

    #: The shape of this container, i.e, (rows, columns).  The items in
    #: **components** are shuffled appropriately to match this
    #: specification.  If there are fewer components than cells, the remaining
    #: cells are filled in with spaces.  If there are more components than cells,
    #: the remainder wrap onto new rows as appropriate.
    shape = Trait((0,0), Either(Tuple, List, Array))

    #: This property exposes the underlying grid structure of the container,
    #: and is the preferred way of setting and reading its contents.
    #: When read, this property returns a Numpy array with dtype=object; values
    #: for setting it can be nested tuples, lists, or 2-D arrays.
    #: The array is in row-major order, so that component_grid[0] is the first
    #: row, and component_grid[:,0] is the first column.  The rows are ordered
    #: from top to bottom.
    component_grid = Property

    # The internal component grid, in row-major order.  This gets updated
    # when any of the following traits change: shape, components, grid_components
    _grid = Array

    _cached_total_size = Any
    _h_size_prefs = Any
    _v_size_prefs = Any

    class SizePrefs(object):
        """ Object to hold size preferences across spans in a particular
        dimension.  For instance, if SizePrefs is being used for the row
        axis, then each element in the arrays below express sizing information
        about the corresponding column.
        """

        # The maximum size of non-resizable elements in the span.  If an
        # element of this array is 0, then its corresponding span had no
        # non-resizable components.
        fixed_lengths = Array

        # The maximum preferred size of resizable elements in the span.
        # If an element of this array is 0, then its corresponding span
        # had no resizable components with a non-zero preferred size.
        resizable_lengths = Array

        # The direction of resizability associated with this SizePrefs
        # object.  If this SizePrefs is sizing along the X-axis, then
        # direction should be "h", and correspondingly for the Y-axis.
        direction = Enum("h", "v")

        # The index into a size tuple corresponding to our orientation
        # (0 for horizontal, 1 for vertical).  This is derived from
        # **direction** in the constructor.
        index = Int(0)

        def __init__(self, length, direction):
            """ Initializes this prefs object with empty arrays of the given
            length and with the given direction. """
            self.fixed_lengths = zeros(length)
            self.resizable_lengths = zeros(length)
            self.direction = direction
            if direction == "h":
                self.index = 0
            else:
                self.index = 1

        def update_from_component(self, component, index):
            """ Given a component at a particular index along this SizePref's
            axis, integrates the component's resizability and sizing information
            into self.fixed_lengths and self.resizable_lengths. """
            resizable = self.direction in component.resizable
            pref_size = component.get_preferred_size()
            self.update_from_pref_size(pref_size[self.index], index, resizable)

        def update_from_pref_size(self, pref_length, index, resizable):
            if resizable:
                if pref_length > self.resizable_lengths[index]:
                    self.resizable_lengths[index] = pref_length
            else:
                if pref_length > self.fixed_lengths[index]:
                    self.fixed_lengths[index] = pref_length

        def get_preferred_size(self):
            return amax((self.fixed_lengths, self.resizable_lengths), axis=0)

        def compute_size_array(self, size):
            """ Given a length along the axis corresponding to this SizePref,
            returns an array of lengths to assign each cell, taking into account
            resizability and preferred sizes.
            """
            # There are three basic cases for each column:
            #   1. size < total fixed size
            #   2. total fixed size < size < fixed size + resizable preferred size
            #   3. fixed size + resizable preferred size < size
            #
            # In all cases, non-resizable components get their full width.
            #
            # For resizable components with non-zero preferred size, the following
            # actions are taken depending on case:
            #   case 1: They get sized to 0.
            #   case 2: They get a fraction of their preferred size, scaled based on
            #           the amount of remaining space after non-resizable components
            #           get their full size.
            #   case 3: They get their full preferred size.
            #
            # For resizable components with no preferred size (indicated in our scheme
            # by having a preferred size of 0), the following actions are taken
            # depending on case:
            #   case 1: They get sized to 0.
            #   case 2: They get sized to 0.
            #   case 3: All resizable components with no preferred size split the
            #           remaining space evenly, after fixed width and resizable
            #           components with preferred size get their full size.
            fixed_lengths = self.fixed_lengths
            resizable_lengths = self.resizable_lengths
            return_lengths = zeros_like(fixed_lengths)

            fixed_size = sum(fixed_lengths)
            fixed_length_indices = fixed_lengths > resizable_lengths
            resizable_indices = resizable_lengths > fixed_lengths
            fully_resizable_indices = (resizable_lengths + fixed_lengths == 0)
            preferred_size = sum(fixed_lengths[fixed_length_indices]) + \
                                    sum(resizable_lengths[~fixed_length_indices])

            # Regardless of the relationship between available space and
            # resizable preferred sizes, columns/rows where the non-resizable
            # component is largest will always get that amount of space.
            return_lengths[fixed_length_indices] = fixed_lengths[fixed_length_indices]

            if size <= fixed_size:
                # We don't use fixed_length_indices here because that mask is
                # just where non-resizable components were larger than resizable
                # ones.  If our allotted size is less than the total fixed size,
                # then we should give all non-resizable components their desired
                # size.
                indices = fixed_lengths > 0
                return_lengths[indices] = fixed_lengths[indices]
                return_lengths[~indices] = 0

            elif size > fixed_size and (fixed_lengths > resizable_lengths).all():
                # If we only have to consider non-resizable lengths, and we have
                # extra space available, then we need to give each column an
                # amount of extra space corresponding to its size.
                desired_space = sum(fixed_lengths)
                if desired_space > 0:
                    scale = size / desired_space
                    return_lengths = (fixed_lengths * scale).astype(int)

            elif size <= preferred_size or not fully_resizable_indices.any():
                # If we don't have enough room to give all the non-fully resizable
                # components their preferred size, or we have more than enough
                # room for them and no fully resizable components to take up
                # the extra space, then we just scale the resizable components
                # up or down based on the amount of extra space available.
                delta_lengths = resizable_lengths[resizable_indices] - \
                                        fixed_lengths[resizable_indices]
                desired_space = sum(delta_lengths)
                if desired_space > 0:
                    avail_space = size - sum(fixed_lengths) #[fixed_length_indices])
                    scale = avail_space / desired_space
                    return_lengths[resizable_indices] = (fixed_lengths[resizable_indices] + \
                            scale * delta_lengths).astype(int)

            elif fully_resizable_indices.any():
                # We have enough room to fit all the non-resizable components
                # as well as components with preferred sizes, and room left
                # over for the fully resizable components.  Give the resizable
                # components their desired amount of space, and then give the
                # remaining space to the fully resizable components.
                return_lengths[resizable_indices] = resizable_lengths[resizable_indices]
                avail_space = size - preferred_size
                count = sum(fully_resizable_indices)
                space = avail_space / count
                return_lengths[fully_resizable_indices] = space

            else:
                raise RuntimeError("Unhandled sizing case in GridContainer")

            return return_lengths


    def get_preferred_size(self, components=None):
        """ Returns the size (width,height) that is preferred for this component.

        Overrides PlotComponent.
        """
        if self.fixed_preferred_size is not None:
            return self.fixed_preferred_size

        if components is None:
            components = self.component_grid
        else:
            # Convert to array; hopefully it is a list or tuple of list/tuples
            components = array(components)

        # These arrays track the maximum widths in each column and maximum
        # height in each row.
        numrows, numcols = self.shape

        no_visible_components = True
        self._h_size_prefs = GridPlotContainer.SizePrefs(numcols, "h")
        self._v_size_prefs = GridPlotContainer.SizePrefs(numrows, "v")
        self._pref_size_cache = {}
        for i, row in enumerate(components):
            for j, component in enumerate(row):
                if not self._should_layout(component):
                    continue
                else:
                    no_visible_components = False
                    self._h_size_prefs.update_from_component(component, j)
                    self._v_size_prefs.update_from_component(component, i)

        total_width = sum(self._h_size_prefs.get_preferred_size()) + self.hpadding
        total_height = sum(self._v_size_prefs.get_preferred_size()) + self.vpadding
        total_size = array([total_width, total_height])

        # Account for spacing.  There are N+1 of spaces, where N is the size in
        # each dimension.
        if self.spacing is None:
            spacing = zeros(2)
        else:
            spacing = array(self.spacing)
        total_spacing = array(components.shape[::-1]) * spacing * 2 * (total_size>0)
        total_size += total_spacing

        for orientation, ndx in (("h", 0), ("v", 1)):
            if (orientation not in self.resizable) and \
               (orientation not in self.fit_components):
                total_size[ndx] = self.outer_bounds[ndx]
            elif no_visible_components or (total_size[ndx] == 0):
                total_size[ndx] = self.default_size[ndx]

        self._cached_total_size = total_size
        if self.resizable == "":
            return self.outer_bounds
        else:
            return self._cached_total_size

    def _do_layout(self):
        # If we don't have cached size_prefs, then we need to call
        # get_preferred_size to build them.
        if self._cached_total_size is None:
            self.get_preferred_size()

        # If we need to fit our components, then rather than using our
        # currently assigned size to do layout, we use the preferred
        # size we computed from our components.
        size = array(self.bounds)
        if self.fit_components != "":
            self.get_preferred_size()
            if "h" in self.fit_components:
                size[0] = self._cached_total_size[0] - self.hpadding
            if "v" in self.fit_components:
                size[1] = self._cached_total_size[1] - self.vpadding

        # Compute total_spacing and spacing, which are used in computing
        # the bounds and positions of all the components.
        shape = array(self._grid.shape).transpose()
        if self.spacing is None:
            spacing = array([0,0])
        else:
            spacing = array(self.spacing)
        total_spacing = spacing * 2 * shape

        # Compute the total space used by non-resizable and resizable components
        # with non-zero preferred sizes.
        widths = self._h_size_prefs.compute_size_array(size[0] - total_spacing[0])
        heights = self._v_size_prefs.compute_size_array(size[1] - total_spacing[1])

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
                if not self._should_layout(component):
                    continue

                r = component.resizable
                x = h_positions[i]
                y = v_positions[j]
                w = widths[i]
                h = heights[j]

                if "v" not in r:
                    # Component is not vertically resizable
                    if valign == "top":
                        y += h - component.outer_height
                    elif valign == "center":
                        y += (h - component.outer_height) / 2
                if "h" not in r:
                    # Component is not horizontally resizable
                    if halign == "right":
                        x += w - component.outer_width
                    elif halign == "center":
                        x += (w - component.outer_width) / 2

                component.outer_position = [x,y]
                bounds = list(component.outer_bounds)
                if "h" in r:
                    bounds[0] = w
                if "v" in r:
                    bounds[1] = h

                component.outer_bounds = bounds
                component.do_layout()

    def _reflow_layout(self):
        """ Re-computes self._grid based on self.components and self.shape.
        Adjusts self.shape accordingly.
        """
        numcells = self.shape[0] * self.shape[1]
        if numcells < len(self.components):
            numrows, numcols = divmod(len(self.components), self.shape[0])
            self.shape = (numrows, numcols)
        grid = array(self.components, dtype=object)
        grid.resize(self.shape)
        grid[grid==0] = None
        self._grid = grid
        self._layout_needed = True

    def _shape_changed(self, old, new):
        self._reflow_layout()

    def __components_changed(self, old, new):
        self._reflow_layout()

    def __components_items_changed(self, event):
        self._reflow_layout()

    def _get_component_grid(self):
        return self._grid

    def _set_component_grid(self, val):
        grid = array(val)
        grid_set = set(grid.flatten())

        # Figure out which of the components in the component_grid are new,
        # and which have been removed.
        existing = set(array(self._grid).flatten())
        new = grid_set - existing
        removed = existing - grid_set

        for component in removed:
            if component is not None:
                component.container = None
        for component in new:
            if component is not None:
                if component.container is not None:
                    component.container.remove(component)
                component.container = self

        self.trait_setq(shape=grid.shape)
        self._components = list(grid.flatten())

        if self._should_compact():
            self.compact()

        self.invalidate_draw()
