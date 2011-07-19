from itertools import chain

from chaco.axis import PlotAxis
from chaco.base_plot_container import BasePlotContainer
from chaco.plot import Plot
from traits.api import DelegatesTo, Instance, Int, List, Property, Tuple


DEFAULT_DRAWING_ORDER = ["background", "image", "underlay",      "plot",
                         "selection", "border", "annotation", "overlay"]


class MultiAxisPlotAxis(PlotAxis):
    """ A very basic wrapper around PlotAxis that works with the
        MultiAxisPlotContainer's layout algorithm.
    """
    def get_preferred_size(self):
        return self.outer_bounds
        
    def _do_layout(self):
        self.x, self.y = self.outer_position
        self.width, self.height = self.outer_bounds


class MultiAxisPlotContainer(BasePlotContainer):
    """
    A plot container that stacks multiple axes around a central plot component.
    """

    draw_order = Instance(list, args=(DEFAULT_DRAWING_ORDER,))

    # Do not use an off-screen backbuffer.
    use_backbuffer = False

    # Cache (width, height) of the container's preferred size.
    _cached_preferred_size = Tuple
    
    # The axis components
    axes = List(Instance(MultiAxisPlotAxis))

    # The central plot component
    plot = Instance(Plot)

    # Padding which includes the axes
    container_padding_left = Property
    container_padding_right = Property
    container_padding_bottom = Property
    container_padding_top = Property
        
    #------------------------------------------------------------------------
    # Private attributes
    #------------------------------------------------------------------------
    _left_axes_size = Int(0)
    _right_axes_size = Int(0)
    _top_axes_size = Int(0)
    _bottom_axes_size = Int(0)
    
    #------------------------------------------------------------------------
    
    def __init__(self, *args, **kwargs):
        super(MultiAxisPlotContainer, self).__init__(*args, **kwargs)

        # Connect a bunch of notifications        
        self.on_trait_change(self._xrange_high_changed,
                             "plot.range2d._xrange._high_setting")
        self.on_trait_change(self._xrange_low_changed,
                             "plot.range2d._xrange._low_setting")
        self.on_trait_change(self._yrange_high_changed,
                             "plot.range2d._yrange._high_setting")
        self.on_trait_change(self._yrange_low_changed,
                             "plot.range2d._yrange._low_setting")

    #------------------------------------------------------------------------
    # Layout-related methods
    #------------------------------------------------------------------------
    
    def get_preferred_size(self):
        """
        Returns the size (width,height) that is preferred for this component.

        Overrides Component
        """

        if self.fixed_preferred_size is not None:
            self._cached_preferred_size = self.fixed_preferred_size
            return self.fixed_preferred_size
        
        horizontal_axes = set([axis for axis in self.axes
                               if axis.orientation in ["left", "right"]])
        vertical_axes = set(self.axes) - horizontal_axes

        no_visible_components = True
        horizontal_size = 0
        vertical_size = 0
        
        for axis in horizontal_axes:
            if not self._should_layout(axis):
                continue
            
            no_visible_components = False
            pref_size = axis.get_preferred_size()
            horizontal_size += pref_size[0]        
        
        for axis in vertical_axes:
            if not self._should_layout(axis):
                continue
            
            no_visible_components = False
            pref_size = axis.get_preferred_size()
            vertical_size += pref_size[1]
        
        plot_size = self.plot.get_preferred_size()
        horizontal_size += plot_size[0]
        vertical_size += plot_size[1]
    
        if ("h" not in self.resizable) and ("h" not in self.fit_components):
            horizontal_size = self.bounds[0]
        elif no_visible_components or (horizontal_size == 0):
            horizontal_size = self.default_size[0]
    
        if ("v" not in self.resizable) and ("v" not in self.fit_components):
            vertical_size = self.bounds[1]
        elif no_visible_components or (vertical_size == 0):
            vertical_size = self.default_size[1]
    
        self._cached_preferred_size = (horizontal_size + self.hpadding,
                                       vertical_size + self.vpadding)

        return self._cached_preferred_size

    def _do_layout(self):
        """ Actually performs a layout (called by do_layout()).
        """
        plot = self.plot
        size = list(self.bounds)
        if self.fit_components != "":
            self.get_preferred_size()
            if "h" in self.fit_components:
                size[0] = self._cached_preferred_size[0] - self.hpadding
            if "v" in self.fit_components:
                size[1] = self._cached_preferred_size[1] - self.vpadding

        left_axes = [axis for axis in self.axes if axis.orientation == "left"]
        bottom_axes = [axis for axis in self.axes if axis.orientation == "bottom"]
        right_axes = [axis for axis in self.axes if axis.orientation == "right"]
        top_axes = [axis for axis in self.axes if axis.orientation == "top"]

        horizontal_fixed_size = 0
        vertical_fixed_size = 0
        horizontal_resizable_axes = []
        vertical_resizable_axes = []
        horizontal_resizable_size = 0
        vertical_resizable_size = 0
        size_prefs = {}
        
        for axis in chain(left_axes, right_axes):
            if not self._should_layout(axis):
                continue
            if "h" not in axis.resizable:
                horizontal_fixed_size += axis.outer_bounds[0]
            else:
                preferred_size = axis.get_preferred_size()
                size_prefs[axis] = preferred_size
                horizontal_resizable_size += preferred_size[0]
                horizontal_resizable_axes.append(axis)
        if "h" not in plot.resizable:
            horizontal_fixed_size += plot.outer_bounds[0]
        else:
            preferred_size = plot.get_preferred_size()
            size_prefs[plot] = preferred_size
            horizontal_resizable_size += preferred_size[0]

        for axis in chain(bottom_axes, top_axes):
            if not self._should_layout(axis):
                continue
            if "v" not in axis.resizable:
                vertical_fixed_size += axis.outer_bounds[1]
            else:
                preferred_size = axis.get_preferred_size()
                size_prefs[axis] = preferred_size
                vertical_resizable_size += preferred_size[1]
                vertical_resizable_axes.append(axis)
        if "v" not in plot.resizable:
            vertical_fixed_size += plot.outer_bounds[1]
        else:
            preferred_size = size_prefs.get(plot, plot.get_preferred_size())
            size_prefs[plot] = preferred_size
            vertical_resizable_size += preferred_size[1]

        widths_dict = {}
        heights_dict = {}
        if horizontal_resizable_axes:
            avail_size = size[0] - horizontal_fixed_size
            if horizontal_resizable_size > 0:
                scale = avail_size / float(horizontal_resizable_size)
                for axis in horizontal_resizable_axes:
                    widths_dict[axis] = int(size_prefs[axis][0] * scale)
            else:
                each_size = int(avail_size / len(horizontal_resizable_axes) + 1)
                for axis in horizontal_resizable_axes:
                    widths_dict[axis] = each_size

        if vertical_resizable_axes:
            avail_size = size[1] - vertical_fixed_size
            if vertical_resizable_size > 0:
                scale = avail_size / float(vertical_resizable_size)
                for axis in vertical_resizable_axes:
                    heights_dict[axis] = int(size_prefs[axis][1] * scale)
            else:
                each_size = int(avail_size / len(vertical_resizable_axes) + 1)
                for axis in vertical_resizable_axes:
                    heights_dict[axis] = each_size

        get_width = lambda x: widths_dict.get(x, x.outer_bounds[0])
        get_height = lambda x: heights_dict.get(x, x.outer_bounds[1])
        self._left_axes_size = sum(get_width(axis) for axis in left_axes)
        self._right_axes_size = sum(get_width(axis) for axis in right_axes)
        self._bottom_axes_size = sum(get_height(axis) for axis in bottom_axes)
        self._top_axes_size = sum(get_height(axis) for axis in top_axes)
        plot_size = (size[0] - self._left_axes_size - self._right_axes_size,
                     size[1] - self._bottom_axes_size - self._top_axes_size)
        
        def _layout_directional(axis, position, layout_direction):
            """
                Compute the size and position of an axis
            """
            if not self._should_layout(axis):
                return 0
    
            index = 0 if layout_direction == "h" else 1
            opposite_index = 1 - index
            opposite_direction = "h" if opposite_index == 0 else "v"
            bounds = [get_width(axis), get_height(axis)]
    
            if (bounds[opposite_index] > size[opposite_index]) or \
               (opposite_direction in axis.resizable):
                # If the axis is resizable in the direction dimension or it
                # exceeds the self bounds, set it to the size of the plot.
                bounds[opposite_index] = plot_size[opposite_index]
    
            axis.outer_position = position
            axis.outer_bounds = bounds
            axis.do_layout()
            return bounds[index]
        
        x_pos = 0
        y_pos = self._bottom_axes_size + plot.padding_bottom
        for axis in left_axes:
            x_pos += _layout_directional(axis, [x_pos, y_pos], "h")
        x_pos += plot_size[0] - 1
        for axis in right_axes:
            x_pos += _layout_directional(axis, [x_pos, y_pos], "h")
        
        x_pos = self._left_axes_size + plot.padding_left
        y_pos = 0
        for axis in bottom_axes:
            y_pos += _layout_directional(axis, [x_pos, y_pos], "v")
        y_pos += plot_size[1]
        for axis in top_axes:
            y_pos += _layout_directional(axis, [x_pos, y_pos], "v")

        if self._should_layout(plot):
            plot.outer_position = [self._left_axes_size, self._bottom_axes_size]
            plot.outer_bounds = list(plot_size)
            plot.do_layout()
        return

    #------------------------------------------------------------------------
    # Trait notifications
    #------------------------------------------------------------------------

    def _axes_items_changed(self, event):
        """ Handle insertion/removal of axes from the container.
        """
        for removed in event.removed:
            try:
                self.remove(removed)
            except RuntimeError:
                # Don't blow up when removing components that aren't resident.
                pass
        for added in event.added:
            self.add(added)
    
    def _plot_changed(self, name, old, new):
        """ Handle insertion/removal of the plot from the container.
        """
        try:
            self.remove(old)
        except RuntimeError:
            # Don't blow up when removing components that aren't resident.
            pass
        self.add(new)

    def _get_container_padding_left(self):
        return self.plot.padding_left + self._left_axes_size

    def _get_container_padding_right(self):
        return self.plot.padding_right + self._right_axes_size

    def _get_container_padding_bottom(self):
        return self.plot.padding_bottom + self._bottom_axes_size

    def _get_container_padding_top(self):
        return self.plot.padding_top + self._top_axes_size

    def _xrange_high_changed(self, new):
        pass

    def _xrange_low_changed(self):
        pass

    def _yrange_high_changed(self):
        pass

    def _yrange_low_changed(self):
        pass

