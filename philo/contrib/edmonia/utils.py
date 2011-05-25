from __future__ import division
import Image


def resize_image(im, width=None, height=None):
	if height is None and width is None:
		return im
	
	if height is None:
		width = int(width)
		height = int(width*(im.size[1]/im.size[0]))
	else:
		height = int(height)
		width = int(height*(im.size[0]/im.size[1]))
	
	if width < im.size[0]:
		return im.resize((width, height), Image.ANTIALIAS)
	else:
		return im.resize((width, height), Image.BICUBIC)


def crop_image(im, ratio):
	if ratio is None:
		return im
	
	new_ratio = ratio[0]/ratio[1]
	old_width, old_height = im.size
	old_ratio = old_width/old_height
	
	if new_ratio > old_ratio:
		# New ratio wider. Cut off the top and bottom of the old image so it's equal.
		originX = 0
		crop_width = old_width
		crop_height = old_width/new_ratio
		originY = (old_height - crop_height)/2
	else:
		originY = 0
		crop_height = old_height
		crop_width = old_height*new_ratio
		originX = (old_width - crop_width)/2
		
	cropBox = (int(originX), int(originY), int(originX + crop_width), int(originY + crop_height))
	return im.crop(cropBox)