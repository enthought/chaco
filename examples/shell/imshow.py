#Standard library imports
import sys
from os import path

#Enthought library imports
from enthought.chaco2.shell import imread, imshow, title, show

#Assemble the path to the image
example_dir = sys.path[0]
image_path = path.join(example_dir, '..', 'basic', 'capitol.jpg')

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