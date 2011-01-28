""" This file contains the ui specifications for the chaco.axis.Axis objects.

    Much of it is defined in re-usable chunks so that elements of it can be
    used in UIs of objects that contain an axis.

"""

# Enthought Imports
from enthought.traits.ui.api import View, Group, VGroup, HGroup, Item, TextEditor

title_group = Group(
                    Item("title", label="Text", editor=TextEditor()),
                    # Fix me: We really don't have an reasonable font editor.
                    #Item("title_font", label="Font", style="custom"),
                    Item("title_color", label="Color", style="simple"),
              )

axis_line_group = Group(
                        Item("axis_line_visible", label="Visible"),
                        Group(
                              Item("axis_line_color", label="Color", style="simple"),
                              Item("axis_line_weight", label="Thickness"),
                              # Line Style
                              enabled_when='object.axis_line_visible==True',
                        ),
                  )

tick_labels_group = Group(
                          # fix me: We need a 'Visible' trait on that determines
                          #         whether tick labels are visible or not.
                          # Visible -- The rest should be in a group that is enabled
                          #            by this.
                          # Fix me: Need an reasonable font editor.
                          #Item("tick_label_font", label="Font"),
                          Item("tick_label_color", label="Color", style="simple"),
                          # Fix me: set the rotation of the label.
                          # Rotation
                          # Fix me: Set the offset (in pixels?) of the label to
                          #         allow people to "bump" them up or down.
                          # Offset
                          # Fix me: Are labels next to the axis or off the side of the
                          #         plot?
                          # relative_to: axis|plot_min|plot_max
                   )

tick_lines_group = Group(
                         Item("tick_visible", label="Visible"),
                         Group(
                               # These are the only non-axis part of the view...
                               HGroup(
                                      # fix me: THe enabled_when is not working
                                      #         correctly. This failure began
                                      #         when we switched to using context.
                                      Item("tick_interval_ui", label="Interval",
                                           enabled_when = "object.tick_interval_auto_ui == False"),
                                      Item("tick_interval_auto_ui", label="Auto"),
                               ),
                               Item("tick_color", label="Color", style="simple"),
                               Item("tick_weight", label="Thickness"),
                               #HGroup(
                                      Item("tick_in", label="Tick in (pixels)"),
                                      Item("tick_out", label="Tick out (pixels)"),
                               #),
                               enabled_when="object.tick_visible==True",
                         ),
                    )

tick_lines_group = Group(
                         Item("tick_visible", label="Visible"),
                         Group(
                               Item("tick_color", label="Color", style="simple"),
                               Item("tick_weight", label="Thickness"),
                               Item("tick_in", label="Tick in (pixels)"),
                               Item("tick_out", label="Tick out (pixels)"),
                               # Fix me: We really need to split out the tick interval
                               #         into a UI like this.
                               #HGroup(
                               #       Item("tick_interval_ui", label="Interval",
                               #            enabled_when = "object.tick_interval_auto_ui == False"),
                               #       Item("tick_interval_auto_ui", label="Auto"),
                               #),
                               Item(label="Note: Tick Interval not currently settable."),
                               enabled_when="object.tick_visible==True",
                         ),
                    )

# We are missing a group to specify the "scale" or "range" setting


# The main view for an axis...

default_view = View(
                    VGroup(Group(title_group, label='Title', show_border=True),
                           Group(axis_line_group, label='Axis Line', show_border=True),
                           HGroup(
                                  Group(tick_lines_group,
                                        label='Tick Lines', show_border=True),
                                  Group(tick_labels_group,
                                        label='Labels', show_border=True),
                                  label='Ticks',
                           ),
                           layout="tabbed",
                    ),
                    buttons = ["OK", "Cancel"],
              )

# Fix me: Should we do something here where we register this with the Axis object?
