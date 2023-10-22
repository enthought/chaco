Chaco Plot Cheat Sheet
======================

.. highlight:: python
  :linenothreshold: 5

.. index:: Cheat Sheet

Data and Data Descriptors
-------------------------

Adding data for a plot::

  myTADP = ArrayPlotData()
  myTADP.set_data( [Variable Name - String],[Data - Array, List, Tuple] )

  # data must evaluate to a list, tuple or numpy array

  # Example
  myTADP = ArrayPlotData()
  myTADP.set_data( 'X',phaseA )
  myTADP.set_data( 'Y',amplitudeA )

Masking Data
------------

You can replace any data with None to not plot the data. Works for the index
and value entries.

Setting the mask values in the ArrayDataSource to False does not filter the
plotted data based upon the True/False states of the particular mask value.

Padding
-------

.. todo:: clarify these snippets

The padding attributes represent the number of pixels set aside around
a plot. The fundamental attributes are

  [padding_left, padding_right, padding_top, padding_bottom]

Retrive the padding using::

  myFirstPlot.myTP.padding
  [50, 50, 50, 50]
  # returns [padding_left, padding_right, padding_top, padding_bottom]

You can also set equal padding by::

  myFirstPlot.myTP.padding = 25
  # results in padding of [25,25,25,25]
  [50, 50, 50, 50]

.. index::
  pair: Color; Alias

Color Aliases
-------------

From enable/colors.py
::

  transparent_color =     (0.0, 0.0, 0.0, 0.0)

  color_table = {
      "aliceblue":           (0.941, 0.973, 1.000, 1.0),
      "antiquewhite":        (0.980, 0.922, 0.843, 1.0),
      "aqua":                (0.000, 1.000, 1.000, 1.0),
      "aquamarine":          (0.498, 1.000, 0.831, 1.0),
      "azure":               (0.941, 1.000, 1.000, 1.0),
      "beige":               (0.961, 0.961, 0.863, 1.0),
      "bisque":              (1.000, 0.894, 0.769, 1.0),
      "black":               (0.000, 0.000, 0.000, 1.0),
      "blanchedalmond":      (1.000, 0.922, 0.804, 1.0),
      "blue":                (0.000, 0.000, 1.000, 1.0),
      "blueviolet":          (0.541, 0.169, 0.886, 1.0),
      "brown":               (0.647, 0.165, 0.165, 1.0),
      "burlywood":           (0.871, 0.722, 0.529, 1.0),
      "cadetblue":           (0.373, 0.620, 0.627, 1.0),
      "chartreuse":          (0.498, 1.000, 0.000, 1.0),
      "chocolate":           (0.824, 0.412, 0.118, 1.0),
      "coral":               (1.000, 0.498, 0.314, 1.0),
      "cornflowerblue":      (0.392, 0.584, 0.929, 1.0),
      "cornsilk":            (1.000, 0.973, 0.863, 1.0),
      "crimson":             (0.863, 0.078, 0.235, 1.0),
      "cyan":                (0.000, 1.000, 1.000, 1.0),
      "darkblue":            (0.000, 0.000, 0.545, 1.0),
      "darkcyan":            (0.000, 0.545, 0.545, 1.0),
      "darkgoldenrod":       (0.722, 0.525, 0.043, 1.0),
      "darkgray":            (0.663, 0.663, 0.663, 1.0),
      "darkgreen":           (0.000, 0.392, 0.000, 1.0),
      "darkgrey":            (0.663, 0.663, 0.663, 1.0),
      "darkkhaki":           (0.741, 0.718, 0.420, 1.0),
      "darkmagenta":         (0.545, 0.000, 0.545, 1.0),
      "darkolivegreen":      (0.333, 0.420, 0.184, 1.0),
      "darkorange":          (1.000, 0.549, 0.000, 1.0),
      "darkorchid":          (0.600, 0.196, 0.800, 1.0),
      "darkred":             (0.545, 0.000, 0.000, 1.0),
      "darksalmon":          (0.914, 0.588, 0.478, 1.0),
      "darkseagreen":        (0.561, 0.737, 0.561, 1.0),
      "darkslateblue":       (0.282, 0.239, 0.545, 1.0),
      "darkslategray":       (0.184, 0.310, 0.310, 1.0),
      "darkslategrey":       (0.184, 0.310, 0.310, 1.0),
      "darkturquoise":       (0.000, 0.808, 0.820, 1.0),
      "darkviolet":          (0.580, 0.000, 0.827, 1.0),
      "deeppink":            (1.000, 0.078, 0.576, 1.0),
      "deepskyblue":         (0.000, 0.749, 1.000, 1.0),
      "dimgray":             (0.412, 0.412, 0.412, 1.0),
      "dimgrey":             (0.412, 0.412, 0.412, 1.0),
      "dodgerblue":          (0.118, 0.565, 1.000, 1.0),
      "firebrick":           (0.698, 0.133, 0.133, 1.0),
      "floralwhite":         (1.000, 0.980, 0.941, 1.0),
      "forestgreen":         (0.133, 0.545, 0.133, 1.0),
      "fuchsia":             (1.000, 0.000, 1.000, 1.0),
      "gainsboro":           (0.863, 0.863, 0.863, 1.0),
      "ghostwhite":          (0.973, 0.973, 1.000, 1.0),
      "gold":                (1.000, 0.843, 0.000, 1.0),
      "goldenrod":           (0.855, 0.647, 0.125, 1.0),
      "gray":                (0.502, 0.502, 0.502, 1.0),
      "green":               (0.000, 0.502, 0.000, 1.0),
      "greenyellow":         (0.678, 1.000, 0.184, 1.0),
      "grey":                (0.502, 0.502, 0.502, 1.0),
      "honeydew":            (0.941, 1.000, 0.941, 1.0),
      "hotpink":             (1.000, 0.412, 0.706, 1.0),
      "indianred":           (0.804, 0.361, 0.361, 1.0),
      "indigo":              (0.294, 0.000, 0.510, 1.0),
      "ivory":               (1.000, 1.000, 0.941, 1.0),
      "khaki":               (0.941, 0.902, 0.549, 1.0),
      "lavender":            (0.902, 0.902, 0.980, 1.0),
      "lavenderblush":       (1.000, 0.941, 0.961, 1.0),
      "lawngreen":           (0.486, 0.988, 0.000, 1.0),
      "lemonchiffon":        (1.000, 0.980, 0.804, 1.0),
      "lightblue":           (0.678, 0.847, 0.902, 1.0),
      "lightcoral":          (0.941, 0.502, 0.502, 1.0),
      "lightcyan":           (0.878, 1.000, 1.000, 1.0),
      "lightgoldenrodyellow":(0.980, 0.980, 0.824, 1.0),
      "lightgray":           (0.827, 0.827, 0.827, 1.0),
      "lightgreen":          (0.565, 0.933, 0.565, 1.0),
      "lightgrey":           (0.827, 0.827, 0.827, 1.0),
      "lightpink":           (1.000, 0.714, 0.757, 1.0),
      "lightsalmon":         (1.000, 0.627, 0.478, 1.0),
      "lightseagreen":       (0.125, 0.698, 0.667, 1.0),
      "lightskyblue":        (0.529, 0.808, 0.980, 1.0),
      "lightslategray":      (0.467, 0.533, 0.600, 1.0),
      "lightslategrey":      (0.467, 0.533, 0.600, 1.0),
      "lightsteelblue":      (0.690, 0.769, 0.871, 1.0),
      "lightyellow":         (1.000, 1.000, 0.878, 1.0),
      "lime":                (0.000, 1.000, 0.000, 1.0),
      "limegreen":           (0.196, 0.804, 0.196, 1.0),
      "linen":               (0.980, 0.941, 0.902, 1.0),
      "magenta":             (1.000, 0.000, 1.000, 1.0),
      "maroon":              (0.502, 0.000, 0.000, 1.0),
      "mediumaquamarine":    (0.400, 0.804, 0.667, 1.0),
      "mediumblue":          (0.000, 0.000, 0.804, 1.0),
      "mediumorchid":        (0.729, 0.333, 0.827, 1.0),
      "mediumpurple":        (0.576, 0.439, 0.859, 1.0),
      "mediumseagreen":      (0.235, 0.702, 0.443, 1.0),
      "mediumslateblue":     (0.482, 0.408, 0.933, 1.0),
      "mediumspringgreen":   (0.000, 0.980, 0.604, 1.0),
      "mediumturquoise":     (0.282, 0.820, 0.800, 1.0),
      "mediumvioletred":     (0.780, 0.082, 0.522, 1.0),
      "midnightblue":        (0.098, 0.098, 0.439, 1.0),
      "mintcream":           (0.961, 1.000, 0.980, 1.0),
      "mistyrose":           (1.000, 0.894, 0.882, 1.0),
      "moccasin":            (1.000, 0.894, 0.710, 1.0),
      "navajowhite":         (1.000, 0.871, 0.678, 1.0),
      "navy":                (0.000, 0.000, 0.502, 1.0),
      "oldlace":             (0.992, 0.961, 0.902, 1.0),
      "olive":               (0.502, 0.502, 0.000, 1.0),
      "olivedrab":           (0.420, 0.557, 0.137, 1.0),
      "orange":              (1.000, 0.647, 0.000, 1.0),
      "orangered":           (1.000, 0.271, 0.000, 1.0),
      "orchid":              (0.855, 0.439, 0.839, 1.0),
      "palegoldenrod":       (0.933, 0.910, 0.667, 1.0),
      "palegreen":           (0.596, 0.984, 0.596, 1.0),
      "paleturquoise":       (0.686, 0.933, 0.933, 1.0),
      "palevioletred":       (0.859, 0.439, 0.576, 1.0),
      "papayawhip":          (1.000, 0.937, 0.835, 1.0),
      "peachpuff":           (1.000, 0.855, 0.725, 1.0),
      "peru":                (0.804, 0.522, 0.247, 1.0),
      "pink":                (1.000, 0.753, 0.796, 1.0),
      "plum":                (0.867, 0.627, 0.867, 1.0),
      "powderblue":          (0.690, 0.878, 0.902, 1.0),
      "purple":              (0.502, 0.000, 0.502, 1.0),
      "red":                 (1.000, 0.000, 0.000, 1.0),
      "rosybrown":           (0.737, 0.561, 0.561, 1.0),
      "royalblue":           (0.255, 0.412, 0.882, 1.0),
      "saddlebrown":         (0.545, 0.271, 0.075, 1.0),
      "salmon":              (0.980, 0.502, 0.447, 1.0),
      "sandybrown":          (0.957, 0.643, 0.376, 1.0),
      "seagreen":            (0.180, 0.545, 0.341, 1.0),
      "seashell":            (1.000, 0.961, 0.933, 1.0),
      "sienna":              (0.627, 0.322, 0.176, 1.0),
      "silver":              (0.753, 0.753, 0.753, 1.0),
      "skyblue":             (0.529, 0.808, 0.922, 1.0),
      "slateblue":           (0.416, 0.353, 0.804, 1.0),
      "slategray":           (0.439, 0.502, 0.565, 1.0),
      "slategrey":           (0.439, 0.502, 0.565, 1.0),
      "snow":                (1.000, 0.980, 0.980, 1.0),
      "springgreen":         (0.000, 1.000, 0.498, 1.0),
      "steelblue":           (0.275, 0.510, 0.706, 1.0),
      "tan":                 (0.824, 0.706, 0.549, 1.0),
      "teal":                (0.000, 0.502, 0.502, 1.0),
      "thistle":             (0.847, 0.749, 0.847, 1.0),
      "tomato":              (1.000, 0.388, 0.278, 1.0),
      "turquoise":           (0.251, 0.878, 0.816, 1.0),
      "violet":              (0.933, 0.510, 0.933, 1.0),
      "wheat":               (0.961, 0.871, 0.702, 1.0),
      "white":               (1.000, 1.000, 1.000, 1.0),
      "whitesmoke":          (0.961, 0.961, 0.961, 1.0),
      "yellow":              (1.000, 1.000, 0.000, 1.0),
      "yellowgreen":         (0.604, 0.804, 0.196, 1.0),

      # Several aliases for transparent
      "clear": transparent_color,
      "transparent": transparent_color,
      "none": transparent_color,

      # Placeholders for system- and toolkit-specific UI colors; the
      # toolkit-dependent code below will fill these with the appropriate
      # values.  These hardcoded defaults are for the Windows Classic
      # theme.
      "sys_window" : (0.83137, 0.81569, 0.78431, 1.0),
  }

.. index::
  pair: Styles; Line
  pair: Alias; Line Styles
  single: Grid; Line Styles

Line Styles
-----------

From enable/enable_traits.py::

  __line_style_trait_values = {
    'solid':     None,
    'dot dash':  array( [ 3.0, 5.0, 9.0, 5.0 ] ),
    'dash':      array( [ 6.0, 6.0 ] ),
    'dot':       array( [ 2.0, 2.0 ] ),
    'long dash': array( [ 9.0, 5.0 ] )
  }

.. index::
  pair: Styles; Cursor
  pair: Alias; Cursor
  single: Cursor; Styles

Cursor Styles
-------------

From enable/enable_traits.py::

  # Valid pointer shape names:
  pointer_shapes = [
     'arrow', 'right arrow', 'blank', 'bullseye', 'char', 'cross', 'hand',
     'ibeam', 'left button', 'magnifier', 'middle button', 'no entry',
     'paint brush', 'pencil', 'point left', 'point right', 'question arrow',
     'right button', 'size top', 'size bottom', 'size left', 'size right',
     'size top right', 'size bottom left', 'size top left', 'size bottom right',
     'sizing', 'spray can', 'wait', 'watch', 'arrow wait'
  ]

.. index:
  pair: Fonts; Alias

Fonts
-----

From kiva_font_traits.py::

  font = KivaFont("modern 10 bold")
  modern
  arial
  courier

  font size

  font attribute = bold italic underline

  # Mapping of strings to valid Kiva font families:
  font_families = {
      'default':    kc.DEFAULT,
      'decorative': kc.DECORATIVE,
      'roman':      kc.ROMAN,
      'script':     kc.SCRIPT,
      'swiss':      kc.SWISS,
      'modern':     kc.MODERN
  }

  # Mapping of strings to Kiva font styles:
  font_styles = {
      'italic': kc.ITALIC
  }

  # Mapping of strings to Kiva font weights:
  font_weights = {
      'bold': kc.BOLD
  }

  default_face = {
          kc.SWISS: "Arial",
          kc.ROMAN: "Times",
          kc.MODERN: "Courier",
          kc.SCRIPT: "Zapfino",
          kc.DECORATIVE: "Zapfino",  # need better choice for this
          }

  # Mapping of strings to valid Kiva font families:
  font_families = {
      'default':    kc.DEFAULT,
      'decorative': kc.DECORATIVE,
      'roman':      kc.ROMAN,
      'script':     kc.SCRIPT,
      'swiss':      kc.SWISS,
      'modern':     kc.MODERN
  }

  # Mapping of strings to Kiva font styles:
  font_styles = {
      'italic': kc.ITALIC
  }

  # Mapping of strings to Kiva font weights:
  font_weights = {
      'bold': kc.BOLD
  }

  default_face = {
          kc.SWISS: "Arial",
          kc.ROMAN: "Times",
          kc.MODERN: "Courier",
          kc.SCRIPT: "Zapfino",
          kc.DECORATIVE: "Zapfino",  # need better choice for this
          }

  def info ( self ):
      return ( "a string describing a font (e.g. '12 pt bold italic "
               "swiss family Arial' or 'default 12')" )

.. index:
  pair: Colormap; Alias

Colormaps
---------
::

  # Make the convenient list of all the function names as well as a dictionary
  # of name->function mappings.  These are useful for UI editors.

  Found in chaco\default_colormaps.py

  color_map_functions = [
      jet,
      autumn,
      bone,
      cool,
      copper,
      flag,
      gray,
      yarg,
      hot,
      hsv,
      pink,
      prism,
      spring,
      summer,
      winter,
      cw1_004,
      cw1_005,
      cw1_006,
      cw1_028,
      gmt_drywet,
      Spectral,
      RdBu,
      RdPu,
      YlGnBu,
      RdYlBu,
      GnBu,
      RdYlGn,
      PuBu,
      BuGn,
      Greens,
      PRGn,
      BuPu,
      OrRd,
      Oranges,
      PiYG,
      YlGn,
      BrBG,
      Reds,
      RdGy,
      PuRd,
      Blues,
      Greys,
      YlOrRd,
      YlOrBr,
      Purples,
      PuOr,
      PuBuGn,
      gist_earth,
      gist_gray,
      gist_heat,
      gist_ncar,
      gist_rainbow,
      gist_stern,
      gist_yarg,
  ]

from default_colors.py::

  """List of nice color palettes for Chaco"""

  # This is a palette of 10 nice colors to use for mapping/discrete
  # color differentiation.  From ColorBrewer.
  cbrewer = [
      (0.65098039,  0.80784314,  0.89019608, 1.0),
      (0.12156863,  0.47058824,  0.70588235, 1.0),
      (0.69803922,  0.8745098 ,  0.54117647, 1.0),
      (0.2       ,  0.62745098,  0.17254902, 1.0),
      (0.98431373,  0.60392157,  0.6       , 1.0),
      (0.89019608,  0.10196078,  0.10980392, 1.0),
      (0.99215686,  0.74901961,  0.43529412, 1.0),
      (1.        ,  0.49803922,  0.        , 1.0),
      (0.79215686,  0.69803922,  0.83921569, 1.0),
      (0.41568627,  0.23921569,  0.60392157, 1.0),
      ]

  palette11 = [
      (0.725490, 0.329412, 0.615686, 1.0),
      (0.121569, 0.313725, 0.552941, 1.0),
      (0.376471, 0.525490, 0.082353, 1.0),
      (0.435294, 0.380392, 0.572549, 1.0),
      (0.988235, 0.400000, 0.600000, 1.0),
      (0.133333, 0.588235, 0.976471, 1.0),
      (0.992157, 0.600000, 0.400000, 1.0),
      (0.611765, 0.200000, 0.380392, 1.0),
      (0.388235, 0.647059, 0.537255, 1.0),
      (0.545098, 0.686275, 0.874510, 1.0),
      (0.623529, 0.501961, 0.862745, 1.0),
      ]

  palette14 = [
      (0.286275, 0.235294, 0.545098, 1.0),
      (0.976471, 0.709804, 0.313725, 1.0),
      (0.850980, 0.094118, 0.521569, 1.0),
      (0.431373, 0.662745, 0.431373, 1.0),
      (0.803922, 0.345098, 0.345098, 1.0),
      (0.015686, 0.749020, 0.403922, 1.0),
      (0.694118, 0.686275, 0.580392, 1.0),
      (0.376471, 0.298039, 0.788235, 1.0),
      (0.992157, 0.396078, 0.011765, 1.0),
      (0.298039, 0.776471, 0.615686, 1.0),
      (0.988235, 0.407843, 0.686275, 1.0),
      (0.000000, 0.600000, 0.984314, 1.0),
      (0.470588, 0.917647, 0.478431, 1.0),
      (0.627451, 0.250980, 0.815686, 1.0),
      ]

  PALETTES = [cbrewer, palette11, palette14]
