from chaco.grid_mapper import GridMapper
from traits.api import HasTraits


class ToolState(HasTraits):

    def __init__(self, prev, next):
        self.prev = prev
        self.next = next

    def apply(self, tool):
        raise NotImplementedError()

    def revert(self, tool):
        raise NotImplementedError()


class GroupedToolState(ToolState):

    def __init__(self, states):
        self.states = states

    def apply(self, tool):
        for state in self.states:
            state.apply(tool)

    def revert(self, tool):
        for state in self.states[::-1]:
            state.revert(tool)


class PanState(ToolState):

    def apply(self, tool):
        if isinstance(tool.component.index_mapper, GridMapper):
            index_mapper = tool.component.index_mapper._xmapper
            value_mapper = tool.component.index_mapper._ymapper
        else:
            index_mapper = tool.component.index_mapper
            value_mapper = tool.component.value_mapper
        if self.next[0] != self.prev[0]:
            high = index_mapper.range.high
            low = index_mapper.range.low
            range = high-low

            index_mapper.range.set_bounds(low=self.next[0] - range/2,
                                          high=self.next[0] + range/2)

        if self.next[1] != self.prev[1]:
            high = value_mapper.range.high
            low = value_mapper.range.low
            range = high-low

            value_mapper.range.set_bounds(low=self.next[1] - range/2,
                                          high=self.next[1] + range/2)

    def revert(self, tool):
        if isinstance(tool.component.index_mapper, GridMapper):
            index_mapper = tool.component.index_mapper._xmapper
            value_mapper = tool.component.index_mapper._ymapper
        else:
            index_mapper = tool.component.index_mapper
            value_mapper = tool.component.value_mapper

        if self.next[0] != self.prev[0]:
            high = index_mapper.range.high
            low = index_mapper.range.low
            range = high-low

            index_mapper.range.set_bounds(low=self.prev[0] - range/2,
                                          high=self.prev[0] + range/2)

        if self.next[1] != self.prev[1]:
            high = value_mapper.range.high
            low = value_mapper.range.low
            range = high-low

            index_mapper.range.set_bounds(low=self.prev[1] - range/2,
                                          high=self.prev[1] + range/2)


class ZoomState(ToolState):
    """ A zoom state which can be applied and reverted.

        This class exists so that subclasses can introduce new types
        of events which can be applied and reverted in the same manner.
        This greatly eases the code for managing history
    """

    def apply(self, zoom_tool):
        index_factor = self.next[0]/self.prev[0]
        value_factor = self.next[1]/self.prev[1]

        if isinstance(zoom_tool.component.index_mapper, GridMapper):
            index_mapper = zoom_tool.component.index_mapper._xmapper
            value_mapper = zoom_tool.component.index_mapper._ymapper
        else:
            index_mapper = zoom_tool.component.index_mapper
            value_mapper = zoom_tool.component.value_mapper

        if index_factor != 1.0:
            zoom_tool._zoom_in_mapper(index_mapper, index_factor)
        if value_factor != 1.0:
            zoom_tool._zoom_in_mapper(value_mapper, value_factor)

        zoom_tool._index_factor = self.next[0]
        zoom_tool._value_factor = self.next[1]

        # TODO: Clip to domain bounds by inserting a pan tool and altering the
        # index factor and value factor

    def revert(self, zoom_tool):
        if isinstance(zoom_tool.component.index_mapper, GridMapper):
            index_mapper = zoom_tool.component.index_mapper._xmapper
            value_mapper = zoom_tool.component.index_mapper._ymapper
        else:
            index_mapper = zoom_tool.component.index_mapper
            value_mapper = zoom_tool.component.value_mapper

        zoom_tool._zoom_in_mapper(index_mapper,
                                  self.prev[0]/self.next[0])
        zoom_tool._zoom_in_mapper(value_mapper,
                                  self.prev[1]/self.next[1])

        zoom_tool._index_factor = self.prev[0]
        zoom_tool._value_factor = self.prev[1]


class SelectedZoomState(ZoomState):

    def apply(self, zoom_tool):
        x_mapper = zoom_tool._get_x_mapper()
        y_mapper = zoom_tool._get_y_mapper()

        x_mapper.range.set_bound(low=self.next[0], high=self.next[1])
        y_mapper.range.set_bound(low=self.next[2], high=self.next[3])

    def revert(self, zoom_tool):
        x_mapper = zoom_tool._get_x_mapper()
        y_mapper = zoom_tool._get_y_mapper()

        x_mapper.range.set_bound(low=self.prev[0], high=self.prev[1])
        y_mapper.range.set_bound(low=self.prev[2], high=self.prev[3])
