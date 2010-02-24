# Standard library imports
import os.path
import sys

# Enthought library imports
from enthought.util.resource import find_resource
from enthought.chaco.shell import imread, imshow, title, show

# Get the image file using the find_resource module
image_path = os.path.join('examples','basic','capitol.jpg')
alt_path = os.path.join('..','basic','capitol.jpg')
image_file = find_resource('Chaco', image_path, alt_path=alt_path)

# Check to see if the image was found
if image_file is None:
    print 'The image "capitol.jpg" could not be found.'
    sys.exit()

# Create the image
image = imread(image_file)

# Create the plot
imshow(image, origin="top left")

# Alternatively, you can call imshow using the path to the image file
#imshow(alt_path)

# Add a title
title("Simple Image Plot")

# This command is only necessary if running from command line
show()
