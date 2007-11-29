
#imports
from numpy import *
from enthought.chaco2.shell import *
from enthought.chaco2.api import ArrayPlotData, ImageData

#Create data
image = imread("../basic/capitol.jpg")

#Create plot
imshow(image, origin="top left")

#Alternatively, call 
#imshow("../basic/capitol.jpg")

#Add a title
title("simple image plot")

#This command is only necessary if running from command line
show()
