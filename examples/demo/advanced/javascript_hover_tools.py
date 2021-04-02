"""
Demo of a javascript inspector tool that shows a black bar over the active
value axis, as well as the values at the current index, with the numbers
shown in the colors matching the legend.

To Use
------
Run Python on this file which will generate six files,
    plot_hover_coords.html
    plot_hover_coords.png
    plot_hover2_coords.png
    hover_coords.js
    plot_hover_coords_png_hover_data.js
    plot_hover2_coords_png_hover_data.js

Alternatively, if you pass in '-e' or '--embedded' on the command-line, then
a single HTML file will be created that has all JavaScript and images
directly embedded into it.

The script should automatically load your webbrowser on the output file,
but if it does not, then manually open the file hover_coords_plot.html in
your browser to see the output.

Author: Judah De Paula <judah@enthought.com>
Date: November 21, 2008.
"""
# Standard library imports
import os, sys, webbrowser, io
from base64 import encodestring

# Major library imports
from PIL import Image
from numpy import arange, searchsorted, where, array, vstack, linspace
from scipy.special import jn

# Chaco imports
from chaco.api \
    import ArrayPlotData, Plot, PlotGraphicsContext, LinePlot
from chaco.example_support import COLOR_PALETTE


#-- Constants -----------------------------------------------------------------
DPI = 72.0


#------------------------------------------------------------------------------
#  File templates:
#     In a real application, these templates should be their own files,
#     and a real templating engine (ex. Mako) would make things more flexible.
#------------------------------------------------------------------------------
html_template_keys = {'filename1' : 'plot_hover_coords.png',
                      'filename2' : 'plot_hover2_coords.png',
                      'file1_src' : 'plot_hover_coords.png',
                      'file2_src' : 'plot_hover2_coords.png',
                      'hover_coords' :'src="hover_coords.js">',
                      'data1' :'src="plot_hover_coords_png_hover_data.js">',
                      'data2' :'src="plot_hover2_coords_png_hover_data.js">' }


# Turns into index.html.
html_template = """
<html>
<head>
    <script type="text/javascript" %(hover_coords)s </script>
    <script type="text/javascript" %(data1)s </script>
    <script type="text/javascript" %(data2)s </script>
</head>
<body>
<!------------------ What gets shown onmouseover. ------------------>
<div id="Hover"
     style="background-color: White; color: Black; padding:
            5px; position: absolute; visibility: hidden;"> 0
</div>

<div id="BlackPixel"
     style="background-color: White; color: Black; padding:
            0px; position: absolute; visibility: hidden;">
     <img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAAAXNSR0IArs4c6QAAAAlwSFlzAAALEwAACxMBAJqcGAAAAAxJREFUCNdjYGBgAAAABAABJzQnCgAAAABJRU5ErkJggg=="
          width="1"
          height="100"
          alt="black_pixel.inline"
          id="black_pixel.inline" />
</div>
<!------------------ Demo plot ------------------------------------->
<div class = "tabbertab">

    <img src="%(file1_src)s"
         alt="%(filename1)s"
         id="%(filename1)s"
         onmouseover="javascript:ShowHovers('%(filename1)s',
                                            'Hover', 'BlackPixel')"
         onmouseout="javascript:HideHovers(event,
                                           'Hover', 'BlackPixel')" />

    <img src="%(file2_src)s"
         alt="%(filename2)s"
         id="%(filename2)s"
         onmouseover="javascript:ShowHovers('%(filename2)s',
                                            'Hover', 'BlackPixel')"
         onmouseout="javascript:HideHovers(event,
                                           'Hover', 'BlackPixel')" />
</div>
</body>
</html>
"""


# Turns into plot_hover_coords_png_hover_data.js
javascript_data_template = """
// Create a new "CursorData" object
obj = Object();
obj.height = %(height)s;
obj.border_width = %(border_width)s;
obj.padding_top = %(padding_top)s + 1;
obj.padding_left = %(padding_left)s;
obj.padding_bottom = %(padding_bottom)s;
obj.colors = Array( %(colors)s );

// Store it in the global CursorData, using the unique array_id as a key.
GlobalCursorData["%(array_id)s"] = obj

// Store all the data in the array
obj.data = Array( %(data_s)s );
"""


# Turns into hover_coords.js.  Absolutely no string substitution is done.
hover_coords_js_file = """
<!------------------ Javascript hover functions ----------------->
<!-- Depends upon *_hover_data.js files.                       -->
<!--------------------------------------------------------------->

/*
   Global variables
*/

// Maps an image name to a CursorData object that contains an array of
// data and plot visual attributes like height, padding, and border width.
GlobalCursorData = Array();

// The hash key into GlobalCursorArray that corresponds to the the current
// plot that the mouse is over.
var CurrentPlotKey = "";

// The ID of the <div> box that contains the cursor line image.
var BoxElementID;

// The ID of the <img> of the cursor line image.
var LineElementID;

// The number of pixels to offset the readout box from cursor position
var _xOffset = 15;
var _yOffset = 15;


/*
   Convert an array of floats into an HTML formatted string ready for
   the screen.
 */
function FormatToHTML(data) {
    var colors = GlobalCursorData[CurrentPlotKey].colors;
    var s = '<font size=2 face="Courier New">';
    for (var count = 0; count < data.length; count++) {
        s = s + '<font color=' + colors[count] + '>' + data[count] + '</font><br>';
    }
    if (data.length > 0) {
        s = s.substr(0, s.length-4);
    }
    s += "</font>"
    return s;
}


/*
   Slightly more clever get x function than the default.  Limited testing.
*/
function GetMouseX(event) {
    if (!event) {
        event = window.event;
    }
    if (event.clientX) {
        return event.clientX +
               (document.documentElement.scrollLeft
                ? document.documentElement.scrollLeft
                : document.body.scrollLeft);
    } else if (event.pageX) {
        return event.pageX;
    } else {
        return 0;
    }
}


/*
   Slightly more clever get y function than the default.  Limited testing.
*/
function GetMouseY(event) {
    if (!event) {
        event = window.event;
    }
    if (event.clientY) {
        return event.clientY +
               (document.documentElement.scrollTop
                ? document.documentElement.scrollTop
                : document.body.scrollTop);
    } else if (event.pageY) {
        return event.pageY;
    } else {
        return 0;
    }
}


/*
   Uses data registered by external *hover_data.js files.

   Cannot figure out how to get relative coordinates.  Have to calculate
   it instead using the reference image element registered with the
   hover IDs.
*/
function ScreenXToImageX(mouseX) {
    var referenceX = document.getElementById(CurrentPlotKey);
    var cursor_data = GlobalCursorData[CurrentPlotKey];
    var relativeX = mouseX - cursor_data.padding_left
                           - cursor_data.border_width
                           - referenceX.x;
    return relativeX;
}


/*
   Uses data registered by external *hover_data.js files.

   The Screen pixel coordinate that the data pixels in the plot start.
*/
function ScreenYPlotStart(event) {
    var referenceElement = document.getElementById(CurrentPlotKey);
    var cursor_data = GlobalCursorData[CurrentPlotKey];
    return referenceElement.y + cursor_data.padding_top
                              + cursor_data.border_width;
}


/*
   Uses data registered by external *hover_data.js files.

   Given the browser X coordinate compute the plot screen X coordinate
   and use that value to index into the data array of plot values for
   that index.
*/
function ScreenXToDataY(mouseX) {
    var dataY;
    var relativeX = ScreenXToImageX(mouseX);
    var cursor_data = GlobalCursorData[CurrentPlotKey];

    if (relativeX >= 0 && relativeX < cursor_data.data.length) {
        dataY = cursor_data.data[relativeX];
    // Hack to have bar hidden on the left and right side of images.
        document.getElementById(LineElementID).style.visibility = 'visible';
        document.getElementById(BoxElementID).style.visibility = 'visible';
    } else {
        dataY = 0;
        // Hack to have bar hidden on the left and right side of images.
        document.getElementById(LineElementID).style.visibility = 'hidden';
        document.getElementById(BoxElementID).style.visibility = 'hidden';
    }
    return dataY;
}


/*
   Uses data registered by external *hover_data.js files.

   Every time the mouse moves over the image, Follow() changes the hovering
   object attributes so they move to the new location.
*/
function Follow(event) {
    // Move the box
    var referenceElement = document.getElementById(CurrentPlotKey);
    var element = document.getElementById(BoxElementID);
    if (element != null) {
        var style = element.style;
        // ScreenXToDataY() hacked to have better control of line visibility.
        //style.visibility = 'visible';
        style.left = (parseInt(GetMouseX(event)) + _xOffset) + 'px';
        style.top = (parseInt(GetMouseY(event)) + _yOffset) + 'px';
    element.innerHTML = FormatToHTML(ScreenXToDataY(GetMouseX(event)));
    }

    // Move the line
    var element = document.getElementById(LineElementID);
    var image_element = document.getElementById("black_pixel.inline");
    if (element != null) {
        var style = element.style;
        // ScreenXToDataY() hacked to have better control of line visibility.
        //style.visibility = 'visible';
        style.left = parseInt(GetMouseX(event)) + 'px';
        style.top = parseInt(ScreenYPlotStart()) + 'px';
        element.height = GlobalCursorData[CurrentPlotKey].height - 1;
        image_element.height = element.height;
    }
}


/*
   Abstracted out Show() that assigns the Follow() to mouse movements.
*/
function Show(referenceElementID) {
    var referenceElement = document.getElementById(referenceElementID);
    if (referenceElement) {
        referenceElement.onmousemove = Follow;
    }
}


/*
   Abstracted out Hide() that assigns the Follow() to mouse movements.
   Turns the hover object invisible and disables the Follow() listener.
   FIXME:  The listener is turned off for both hover objects even though
   only one object is hidden by this call.
*/
function Hide(referenceElementID, elementID) {
    var divStyle = document.getElementById(elementID).style;
    var referenceElement = document.getElementById(referenceElementID);
    divStyle.visibility = 'hidden';
    referenceElement.onmousemove = '';
}


/*
   Main entry point for onmouseover event of images.  Sets the globals
   to the active image the mouse just entered and turns on the hovers.
*/
function ShowHovers(referenceElementID, boxElementID, lineElementID) {
    //_dataIndex = plot_names.indexOf(referenceElementID);
    CurrentPlotKey = referenceElementID;
    BoxElementID = boxElementID;
    LineElementID = lineElementID;
    Show(CurrentPlotKey);
    Show(CurrentPlotKey);
}


/*
   Main event call point for onmouseout event for images
*/
function HideHovers(event, boxElementID, lineElementID) {
    var relatedTarget = event.relatedTarget;
    if ((relatedTarget == null) ||
        (relatedTarget.id != boxElementID) &&
        (relatedTarget.id != lineElementID) &&
        (relatedTarget.id != 'black_pixel.inline')) {
        Hide(CurrentPlotKey, boxElementID);
        Hide(CurrentPlotKey, lineElementID);
    }
}
"""


#------------------------------------------------------------------------------
#  Data generation functions for *_hover_data.js files.
#------------------------------------------------------------------------------

def get_pixel_data(segment, renderer, screen_width):
    """
    Take a segment of points and use a renderer to map them to screen coords.

    Algorithm
    ---------
    Fast little function that only works if the samples are sorted.
    FIXME: Need more explanation.
    """
    screen_points = renderer.map_screen(segment)

    if len(screen_points) == 0:
        return array([])

    s_index = screen_points[:,0].astype(int)
    d_value = segment[:,1]
    if len(s_index) != len(d_value):
        raise ValueError('Data-to-screen mapping not 1-to-1.')
    indices = searchsorted(s_index, arange(0, screen_width))
    indices[where(indices == 0)] = 1
    return d_value[indices-1]


def write_hover_coords(container, array_id, script_filename=None):
    """
    Create a JavaScript formatted file of screen index to data values.

    Parameters
    ----------
    container : Plot
        Chaco container object such as a plot that contain renderers
        and border padding information.
    array_id : str
        An identifier that will be used as the key when assigning the
        data array to the global list of data arrays.  This identifier
        should be unique among all the scripts that will be loaded in
        a single HTML file.
    script_filename : str
        Full path to the desired output javascript file.  If no name
        is passed in, then no file is written.

    Returns
    -------
    Returns the JavaScript data file as a string.

    Description
    -----------
    To have a PNG plot show the values of the curves in a browser,
    JavaScript is used to get the screen X/Y and convert the X into the
    corresponding plot data values.  This function creates that mapping
    array.  A couple of extra padding variables are also exported so the
    JavaScript can do some additional offset calculations.
    """
    screen_width = container.width
    # For every renderer in the plot, create an array of the same length
    # as the screen width that contains the data value for each screen
    # position.  Stack all of these arrays together into the 2D 'pixel_data'
    # array, then pass it into the template for the hover_data javascript file.
    segment_data = []
    colors = []
    for renderer_name in sorted(container.legend.plots.keys()):
        renderer = container.legend.plots[renderer_name][0]
        data_points = renderer._cached_data_pts
        if not isinstance(renderer, LinePlot):
            data_points = [data_points]
        for segment in data_points:
            segment_data.append(get_pixel_data(segment, renderer, screen_width))
        colors.append(renderer.color_)

    if len(segment_data) > 0:
        pixel_data = vstack(segment_data).T
    else:
        pixel_data = array([]).reshape(0, 2)

    # Fill out a template using the just-created data.
    colstrings = []
    for color in colors:
        if len(color) == 4:
            alpha = color[3]
        else:
            alpha = 1
        r, g, b = [int(component * alpha * 255) for component in color[:3]]
        colstrings.append('"#%02x%02x%02x"' % (r,g,b))
    colors = ",".join(colstrings);

    line_template = ",".join(['"%1.2f"'] * pixel_data.shape[1])
    data_s = ''
    for row in pixel_data[:-1]:
        data_s += '[' + line_template % tuple(row) +  '],'
    if len(pixel_data) > 0:
        data_s += '[' + line_template % tuple(row) + ']'

    template_keys = dict(height = container.height,
                         padding_top = container.padding_top,
                         padding_left = container.padding_left,
                         padding_bottom = container.padding_bottom,
                         border_width = container.border_width,
                         array_id = array_id,
                         pixel_data = pixel_data,
                         colors = colors,
                         data_s = data_s)

    # Write out and return the result.
    output = javascript_data_template % template_keys
    if script_filename:
        f = open(script_filename, 'wt')
        f.write(output)
        f.close()

    return output


#------------------------------------------------------------------------------
#  Plot and renderer generation functions.
#------------------------------------------------------------------------------
def create_plot(num_plots=8, type='line'):
    """ Create a single plot object, with multiple renderers. """
    # This is a bit of a hack to work around that line widths don't scale
    # with the GraphicsContext's CTM.
    dpi_scale = DPI / 72.0
    numpoints = 100
    low = -5
    high = 15.0
    x = linspace(low, high, numpoints)
    pd = ArrayPlotData(index=x)
    p = Plot(pd, bgcolor="white", padding=50, border_visible=True)
    for i in range(1,num_plots+2):
        pd.set_data("y" + str(i), jn(i,x))
        p.plot(("index", "y" + str(i)), color=tuple(COLOR_PALETTE[i]),
               width = 2.0 * dpi_scale, type=type)
    p.x_grid.visible = True
    p.x_grid.line_width *= dpi_scale
    p.y_grid.visible = True
    p.y_grid.line_width *= dpi_scale
    p.legend.visible = True
    return p


def draw_plot(filename, size=(800,600), num_plots=8, type='line', key=''):
    """ Save the plot, and generate the hover_data file. """
    container = create_plot(num_plots, type)
    container.outer_bounds = list(size)
    container.do_layout(force=True)
    gc = PlotGraphicsContext(size, dpi=DPI)
    gc.render_component(container)
    if filename:
        gc.save(filename)
        script_filename = filename[:-4] + "_png_hover_data.js"
    else:
        script_filename = None
    plot = make_palettized_png_str(gc)
    script_data = write_hover_coords(container, key, script_filename)
    return (plot, script_data)


def make_palettized_png_str(gc):
    """ Generate a png file in a string, base64 encoded. """
    format = gc.format()[:-2].upper()
    if format != "RGBA":
        gc = gc.convert_pixel_format("rgba32")
    img = Image.fromstring("RGBA",
                           (gc.width(), gc.height()), gc.bmp_array.tostring())
    img2 = img.convert("P")
    output_buf = io.StringIO()
    img2.save(output_buf, 'png')
    output = encodestring(output_buf.getvalue())
    output_buf.close()
    return output


#------------------------------------------------------------------------------
#  Main
#------------------------------------------------------------------------------
def main(embedded=False):
    """
    Create the files and load the output in a webbrowser.
    """
    # 1. Create the JavaScript hover tool file.
    #    Only doing this to keep the demo file self-contained.
    target_path = os.path.join(os.getcwd(), 'hover_coords.js')
    if embedded:
        html_template_keys['hover_coords'] = '>\n%s\n' % hover_coords_js_file
    else:
        f = open(target_path, 'wt')
        f.write(hover_coords_js_file)
        f.close()

    # 2. Create the dynamically generated JavaScript data files.
    if embedded:
        html_template_keys['file1_src'] = None
        html_template_keys['file2_src'] = None
    file1_strs = draw_plot(html_template_keys['file1_src'],
                           size=(800, 600),
                           key=html_template_keys['filename1'])
    file2_strs = draw_plot(html_template_keys['file2_src'],
                           size=(600, 400),
                           num_plots = 4,
                           type='scatter',
                           key=html_template_keys['filename2'])

    # 3. Choose the correct src type for the HTML file if embedded.
    if embedded:
        src1 = 'data:image/png;base64,' + file1_strs[0]
        html_template_keys['file1_src'] = src1
        src2 = 'data:image/png;base64,' + file2_strs[0]
        html_template_keys['file2_src'] = src2
        html_template_keys['data1'] = '>\n%s\n' % file1_strs[1]
        html_template_keys['data2'] = '>\n%s\n' % file2_strs[1]

    # 4. Create the HTML file.
    out_html = os.path.join(os.getcwd(), 'plot_hover_coords.html')
    f = open(out_html, 'wt')
    f.write(html_template % html_template_keys)
    f.close()

    # 5. Load the finished product.
    try:
        webbrowser.open(out_html)
    except Exception as e:
        print('Browser did not open properly.  Exception %s.  The results' \
              'can be viewed with the file plot_hover_coords.html.' % str(e))
        raise


#===============================================================================
# # Demo class that is used by the demo.py application.
#===============================================================================
# NOTE: The Demo class is being created for the purpose of running this
# example using a TraitsDemo-like app (see examples/demo/demo.py in Traits3).
# The demo.py file looks for a 'demo' or 'popup' or 'modal popup' keyword
# when it executes this file, and displays a view for it.

# NOTE2: In this case, Demo class is just a mock object. Essentially we want to
# execute main instead of displaying a UI for Demo: so we hack this by
# overriding configure_traits and edit_traits to return a blank UI.

from traits.api import HasTraits
from traitsui.api import UI, Handler

class Demo(HasTraits):

    def configure_traits(self, *args, **kws):
        main(embedded=True)
        return True

    def edit_traits(self, *args, **kws):
        main(embedded=True)
        return UI(handler=Handler())

popup = Demo()

if __name__ == "__main__":
    if '-e' in sys.argv or '--embedded' in sys.argv:
        main(embedded=True)
    else:
        main(embedded=False)
