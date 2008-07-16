#Standard library imports
import os, sys

#Enthought library imports
from enthought.chaco2.shell import imread, imshow, title, show

#Assemble the path to the image
image_path = os.path.join(sys.path[0], '..', 'basic', 'capitol.jpg')

#Create data
image = imread(image_path)

#Create plot
imshow(image, origin="top left")

#Alternatively, call 
#imshow(image_path)

#Add a title
title("simple image plot")

#This command is only necessary if running from command line
show()