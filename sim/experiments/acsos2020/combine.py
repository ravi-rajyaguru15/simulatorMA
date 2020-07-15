import glob
import cv2
import imutils
import matplotlib.image as mpimg
import pdf2image
import numpy as np

from sim.simulations import localConstants

filemask = "%s*.png" % localConstants.OUTPUT_DIRECTORY
print(filemask)
images = glob.glob(filemask)
print(images)

out = cv2.VideoWriter('outpy.avi',cv2.VideoWriter_fourcc('M','J','P','G'), 10, (1000,1000))

for img in images[1:]:
	pic = cv2.imread(img)
	out.write(pic)
	# print(pic)
	# cv2.imshow('name', pic)
	# cv2.waitKey()

# out.close()