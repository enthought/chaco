""" Defines the TraitsUI view for a PlotAxis """
from traits.api import TraitError
from traitsui.api import View, HGroup, Group, VGroup, Item, TextEditor


def float_or_auto(val):
    """
    Validator function that returns *val* if *val* is either a number or
    the word 'auto'.  This is used as a validator for the text editor
    in the TraitsUI for the **tick_interval** trait.
    """
    try:
        return float(val)
    except:
        if isinstance(val, str) and val == "auto":
            return val
    raise TraitError("Tick interval must be a number or 'auto'.")


# TraitsUI for a PlotAxis.
AxisView = View(
    VGroup(
        Group(
            Item("object.mapper.range.low", label="Low Range"),
            Item("object.mapper.range.high", label="High Range"),
        ),
        Group(
            Item("title", label="Title", editor=TextEditor()),
            Item("title_font", label="Font", style="simple"),
            Item("title_color", label="Color", style="custom"),
            Item(
                "tick_interval",
                label="Interval",
                editor=TextEditor(evaluate=float_or_auto),
            ),
            label="Main",
        ),
        Group(
            Item("tick_color", label="Color", style="custom"),
            Item("tick_weight", label="Thickness"),
            Item("tick_label_color", label="Label color", style="custom"),
            HGroup(
                Item("tick_in", label="Tick in"),
                Item("tick_out", label="Tick out"),
            ),
            Item("tick_visible", label="Visible"),
            label="Ticks",
        ),
        Group(
            Item("axis_line_color", label="Color", style="custom"),
            Item("axis_line_weight", label="Thickness"),
            Item("axis_line_visible", label="Visible"),
            label="Line",
        ),
    ),
    buttons=["OK", "Cancel"],
)
