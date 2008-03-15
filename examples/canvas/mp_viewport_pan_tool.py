
from enthought.traits.api import Int
from enthought.enable2.tools.api import ViewportPanTool

class MPViewportPanTool(ViewportPanTool):

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
            ViewportPanTool.drag_start(self, event)
        return

    def drag_end(self, event):
        if hasattr(event, "bid"):
            event.window.release_blob(event.bid)
        self.event_state = "normal"
        ViewportPanTool.drag_end(self, event)

