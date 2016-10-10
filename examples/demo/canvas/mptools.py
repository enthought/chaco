""" A collection of Chaco tools that respond to a multi-pointer interface
"""
from numpy import asarray, dot, sqrt

# Enthought library imports
from traits.api import Delegate, Dict, Enum, Instance, Int, Property, Trait, Tuple, CArray

# Chaco imports
from chaco.api import BaseTool
from chaco.tools.api import PanTool, DragZoom, LegendTool, RangeSelection


BOGUS_BLOB_ID = -1

def l2norm(v):
    return sqrt(dot(v,v))

class MPPanTool(PanTool):
    cur_bid = Int(BOGUS_BLOB_ID)

    def normal_blob_down(self, event):
        if self.cur_bid == BOGUS_BLOB_ID:
            self.cur_bid = event.bid
            self._start_pan(event, capture_mouse=False)
            event.window.capture_blob(self, event.bid, event.net_transform())

    def panning_blob_up(self, event):
        if event.bid == self.cur_bid:
            self.cur_bid = BOGUS_BLOB_ID
            self._end_pan(event)

    def panning_blob_move(self, event):
        if event.bid == self.cur_bid:
            self._dispatch_stateful_event(event, "mouse_move")

    def panning_mouse_leave(self, event):
        """ Handles the mouse leaving the plot when the tool is in the 'panning'
        state.

        Don't end panning.
        """
        return

    def _end_pan(self, event):
        if hasattr(event, "bid"):
            event.window.release_blob(event.bid)
        PanTool._end_pan(self, event)


class MPDragZoom(DragZoom):

    speed = 1.0

    # The original dataspace points where blobs 1 and 2 went down
    _orig_low = CArray #Trait(None, None, Tuple)
    _orig_high = CArray #Trait(None, None, Tuple)

    # Dataspace center of the zoom action
    _center_pt = Trait(None, None, Tuple)

    # Maps blob ID numbers to the (x,y) coordinates that came in.
    _blobs = Dict()

    # Maps blob ID numbers to the (x0,y0) coordinates from blob_move events.
    _moves = Dict()

    # Properties to convert the dictionaries to map from blob ID numbers to
    # a single coordinate appropriate for the axis the range selects on.
    _axis_blobs = Property(Dict)
    _axis_moves = Property(Dict)

    def _convert_to_axis(self, d):
        """ Convert a mapping of ID to (x,y) tuple to a mapping of ID to just
        the coordinate appropriate for the selected axis.
        """
        if self.axis == 'index':
            idx = self.axis_index
        else:
            idx = 1-self.axis_index
        d2 = {}
        for id, coords in list(d.items()):
            d2[id] = coords[idx]
        return d2

    def _get__axis_blobs(self):
        return self._convert_to_axis(self._blobs)

    def _get__axis_moves(self):
        return self._convert_to_axis(self._moves)

    def drag_start(self, event, capture_mouse=False):
        bid1, bid2 = sorted(self._moves)
        xy01, xy02 = self._moves[bid1], self._moves[bid2]
        self._orig_low, self._orig_high = list(map(asarray,
            self._map_coordinate_box(xy01, xy02)))
        self.orig_center = (self._orig_high + self._orig_low) / 2.0
        self.orig_diag = l2norm(self._orig_high - self._orig_low)

        #DragZoom.drag_start(self, event, capture_mouse)
        self._original_xy = xy02
        c = self.component
        self._orig_screen_bounds = ((c.x,c.y), (c.x2,c.y2))
        self._original_data = (c.x_mapper.map_data(xy02[0]), c.y_mapper.map_data(xy02[1]))
        self._prev_y = xy02[1]
        if capture_mouse:
            event.window.set_pointer(self.drag_pointer)

    def normal_blob_down(self, event):
        if len(self._blobs) < 2:
            self._blobs[event.bid] = (event.x, event.y)
            event.window.capture_blob(self, event.bid,
                transform=event.net_transform())
            event.handled = True

    def normal_blob_up(self, event):
        self._handle_blob_leave(event)

    def normal_blob_move(self, event):
        self._handle_blob_move(event)

    def normal_blob_frame_end(self, event):
        if len(self._moves) == 2:
            self.event_state = "dragging"
            self.drag_start(event, capture_mouse=False)

    def dragging_blob_move(self, event):
        self._handle_blob_move(event)

    def dragging_blob_frame_end(self, event):
        # Get dataspace coordinates of the previous and new coordinates
        bid1, bid2 = sorted(self._moves)
        p1, p2 = self._blobs[bid1], self._blobs[bid2]
        low, high = list(map(asarray, self._map_coordinate_box(p1, p2)))

        # Compute the amount of translation
        center = (high + low) / 2.0
        translation = center - self.orig_center

        # Computing the zoom factor.  We have the coordinates of the original
        # blob_down events, and we have a new box as well.  For now, just use
        # the relative sizes of the diagonals.
        diag = l2norm(high - low)
        zoom = self.speed * self.orig_diag / diag

        # The original screen bounds are used to test if we've reached max_zoom
        orig_screen_low, orig_screen_high = \
                list(map(asarray, self._map_coordinate_box(*self._orig_screen_bounds)))
        new_low = center - zoom * (center - orig_screen_low) - translation
        new_high = center + zoom * (orig_screen_high - center) - translation

        for ndx in (0,1):
            if self._zoom_limit_reached(orig_screen_low[ndx],
                    orig_screen_high[ndx], new_low[ndx], new_high[ndx]):
                return

        c = self.component
        c.x_mapper.range.set_bounds(new_low[0], new_high[0])
        c.y_mapper.range.set_bounds(new_low[1], new_high[1])

        self.component.request_redraw()

    def dragging_blob_up(self, event):
        self._handle_blob_leave(event)

    def _handle_blob_move(self, event):
        if event.bid not in self._blobs:
            return
        self._blobs[event.bid] = event.x, event.y
        self._moves[event.bid] = event.x0, event.y0
        event.handled = True

    def _handle_blob_leave(self, event):
        if event.bid in self._blobs:
            del self._blobs[event.bid]
            self._moves.pop(event.bid, None)
            event.window.release_blob(event.bid)
        if len(self._blobs) < 2:
            self.event_state = "normal"


class MPPanZoom(BaseTool):
    """ This tool wraps a pan and a zoom tool, and automatically switches
    behavior back and forth depending on how many blobs are tracked on
    screen.
    """

    pan = Instance(MPPanTool)

    zoom = Instance(MPDragZoom)

    event_state = Enum("normal", "pan", "zoom")

    _blobs = Delegate('zoom')
    _moves = Delegate('zoom')

    def _dispatch_stateful_event(self, event, suffix):
        self.zoom.dispatch(event, suffix)
        event.handled = False
        self.pan.dispatch(event, suffix)
        if len(self._blobs) == 2:
            self.event_state = 'zoom'
        elif len(self._blobs) == 1:
            self.event_state = 'pan'
        elif len(self._blobs) == 0:
            self.event_state = 'normal'
        else:
            assert len(self._blobs) <= 2
        if suffix == 'blob_up':
            event.window.release_blob(event.bid)
        elif suffix == 'blob_down':
            event.window.release_blob(event.bid)
            event.window.capture_blob(self, event.bid, event.net_transform())
            event.handled = True

    def _component_changed(self, old, new):
        self.pan.component = new
        self.zoom.component = new

    def _pan_default(self):
        return MPPanTool(self.component)

    def _zoom_default(self):
        return MPDragZoom(self.component)


class MPLegendTool(LegendTool):

    event_state = Enum("normal", "dragging")

    cur_bid = Int(-1)

    def normal_blob_down(self, event):
        if self.cur_bid == -1 and self.is_draggable(event.x, event.y):
            self.cur_bid = event.bid
            self.drag_start(event)

    def dragging_blob_up(self, event):
        if event.bid == self.cur_bid:
            self.cur_bid = -1
            self.drag_end(event)

    def dragging_blob_move(self, event):
        if event.bid == self.cur_bid:
            self.dragging(event)

    def drag_start(self, event):
        if self.component:
            self.original_padding = self.component.padding
            if hasattr(event, "bid"):
                event.window.capture_blob(self, event.bid,
                                          event.net_transform())
            else:
                event.window.set_mouse_owner(self, event.net_transform())
            self.mouse_down_position = (event.x,event.y)
            self.event_state = "dragging"
            event.handled = True
        return

    def drag_end(self, event):
        if hasattr(event, "bid"):
            event.window.release_blob(event.bid)
        self.event_state = "normal"
        LegendTool.drag_end(self, event)



class MPRangeSelection(RangeSelection):

    # Maps blob ID numbers to the (x,y) coordinates that came in.
    _blobs = Dict()

    # Maps blob ID numbers to the (x0,y0) coordinates from blob_move events.
    _moves = Dict()

    # Properties to convert the dictionaries to map from blob ID numbers to
    # a single coordinate appropriate for the axis the range selects on.
    _axis_blobs = Property(Dict)
    _axis_moves = Property(Dict)

    def _convert_to_axis(self, d):
        """ Convert a mapping of ID to (x,y) tuple to a mapping of ID to just
        the coordinate appropriate for the selected axis.
        """
        if self.axis == 'index':
            idx = self.axis_index
        else:
            idx = 1-self.axis_index
        d2 = {}
        for id, coords in list(d.items()):
            d2[id] = coords[idx]
        return d2

    def _get__axis_blobs(self):
        return self._convert_to_axis(self._blobs)

    def _get__axis_moves(self):
        return self._convert_to_axis(self._moves)

    def normal_blob_down(self, event):
        if len(self._blobs) < 2:
            self._blobs[event.bid] = (event.x, event.y)
            event.window.capture_blob(self, event.bid,
                transform=event.net_transform())
            event.handled = True

    def normal_blob_up(self, event):
        self._handle_blob_leave(event)

    def normal_blob_frame_end(self, event):
        if len(self._blobs) == 2:
            self.event_state = "selecting"
            #self.drag_start(event, capture_mouse=False)
            #self.selecting_mouse_move(event)
            self._set_sizing_cursor(event)
            self.selection = sorted(self._axis_blobs.values())

    def selecting_blob_move(self, event):
        if event.bid in self._blobs:
            self._blobs[event.bid] = event.x, event.y
            self._moves[event.bid] = event.x0, event.y0

    def selecting_blob_up(self, event):
        self._handle_blob_leave(event)

    def selecting_blob_frame_end(self, event):
        if self.selection is None:
            return
        elif len(self._blobs) == 2:
            axis_index = self.axis_index
            low = self.plot.position[axis_index]
            high = low + self.plot.bounds[axis_index] - 1
            p1, p2 = list(self._axis_blobs.values())
            # XXX: what if p1 or p2 is out of bounds?
            m1 = self.mapper.map_data(p1)
            m2 = self.mapper.map_data(p2)
            low_val = min(m1, m2)
            high_val = max(m1, m2)
            self.selection = (low_val, high_val)
            self.component.request_redraw()
        elif len(self._moves) == 1:
            id, p0 = list(self._axis_moves.items())[0]
            m0 = self.mapper.map_data(p0)
            low, high = self.selection
            if low <= m0 <= high:
                m1 = self.mapper.map_data(self._axis_blobs[id])
                dm = m1 - m0
                self.selection = (low+dm, high+dm)

    def selected_blob_down(self, event):
        if len(self._blobs) < 2:
            self._blobs[event.bid] = (event.x, event.y)
            event.window.capture_blob(self, event.bid,
                transform=event.net_transform())
            event.handled = True

    def selected_blob_move(self, event):
        if event.bid in self._blobs:
            self._blobs[event.bid] = event.x, event.y
            self._moves[event.bid] = event.x0, event.y0

    def selected_blob_frame_end(self, event):
        self.selecting_blob_frame_end(event)

    def selected_blob_up(self, event):
        self._handle_blob_leave(event)

    def _handle_blob_leave(self, event):
        self._moves.pop(event.bid, None)
        if event.bid in self._blobs:
            del self._blobs[event.bid]
            event.window.release_blob(event.bid)

        # Treat the blob leave as a selecting_mouse_up event
        self.selecting_right_up(event)

        if len(self._blobs) < 2:
            self.event_state = "selected"

