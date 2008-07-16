# Standard library imports
import os, sys

# Enthought library imports
from enthought.chaco2.shell import imread, imshow, title, show

# Instantiate the 'image' object so that we can check later if it was set or not
image = None

try:
    # Get the image using the pkg_resources resource_stream module, which will
    # find the file by getting the Chaco install path and appending the image
    # path. This method works in all cases as long as setuptools is installed.
    # If setuptools isn't installed, the backup sys.path[0] method is used
    from pkg_resources import resource_stream, Requirement
    requirement = Requirement.parse('Chaco')
    image_path = os.path.join('examples', 'basic', 'capitol.jpg')
    file_object = resource_stream(requirement, image_path)
    image = imread(file_object)
except:
    # Setuptools was either not installed, or it failed to find the image file.
    # Get the image using sys.path[0], which is the directory that the example
    # lives in. The path to the image is then constructed by navigating from the
    # scripts location. This method only works if this example is called
    # directly from the command line using 'python %SOMEPATH%/imshow.py'
    image_path = os.path.join(sys.path[0], '..', 'basic', 'capitol.jpg')
    try:
        image = imread(image_path)
    except:
        # The image wasn't found at the path specified
        pass

# Check to see if the image was found
if image is None:
    print 'The image "capitol.jpg" could not be found.'
    sys.exit()

# Create plot
imshow(image, origin="top left")

# Alternatively, you can call imshow using the path to the image file
#imshow(image_path)

# Add a title
title("Simple Image Plot")

# This command is only necessary if running from command line
show()