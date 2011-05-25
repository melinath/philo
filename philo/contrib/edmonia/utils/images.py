import Image


IMAGE_CACHE_TIME = 60


class ResizeError(Exception):
	""""An exception that is raised if a resized image cannot be constructed from
	the input."""
	pass


def get_resize_dimensions(im, width=None, height=None):
	"""Returns a (width, height) tuple for the resized image, or None if no
	resizing should take place. Constrains proportions if only one of width or
	height is passed in."""
	if height is None and width is None:
		raise ResizeError
	
	x, y = im.size
	
	if height is None:
		height = int(width*(float(y)/x))
		width = int(width)
	elif width is None:
		width = int(height*(float(x)/y))
		height = int(height)
	
	if width <= 0 or height <= 0:
		raise ResizeError
	
	if width == x and height == y:
		return None
	
	return width, height


### Scaling functions
def scale(im, width=None, height=None):
	"""Naively scales and returns a copy of an image with no respect for
	content."""
	im = im.copy()
	
	dimensions = get_resize_dimensions(im, width, height)
	
	if dimensions is None:
		return im
	
	width, height = dimensions
	
	# Choose a method based on whether we're upscaling or downscaling.
	if width < im.size[0]:
		method = Image.ANTIALIAS
	else:
		method = Image.BICUBIC
	
	return im.resize((width, height), method)


### Cropping functions
def get_protected_dimensions(protected):
	x1 = x2 = y1 = y2 = None
	
	for area in protected:
		if x1 is None:
			x1 = area.x1
		else:
			x1 = min(area.x1, x1)
		
		if y1 is None:
			y1 = area.y1
		else:
			y1 = min(area.y1, y1)
		
		x2 = max(area.x2, x2)
		y2 = max(area.y2, y2)
	
	return x1, y1, x2, y2


def get_crop_dimensions(im, ratio=None, protected=None):
	"""Given an image and a ratio, returns the width and height of the crop
	necessary to fit the image to the ratio."""
	if ratio is None or ratio == im.size or ratio == (None, None):
		return im.size
	
	width, height = im.size
	old_ratio = float(width)/height
	
	rwidth, rheight = ratio
	
	if rwidth is None or rheight is None:
		if protected:
			x1, y1, x2, y2 = get_protected_dimensions(protected)
			min_width, min_height = x2 - x1, y2 - y1
		
			if rwidth is None:
				rheight = max(rheight, min_height)
			elif rheight is None:
				rwidth = max(rwidth, min_width)
	
		if rwidth is None:
			rwidth = rheight * old_ratio
		elif rheight is None:
			rheight = rwidth / old_ratio
	
	ratio = float(rwidth)/rheight
	
	if ratio > old_ratio:
		# New ratio is wider. Cut the height.
		return width, int(width/ratio)
	else:
		return int(height*ratio), height


def get_optimal_crop_dimensions(im, width, height, protected):
	"Finds an optimal crop for a given image, width, height, and protected areas."
	min_penalty = None
	coords = None
	
	def get_penalty(area, x1, y1):
		x2 = x1 + width
		y2 = y1 + height
		if area.x1 >= x1 and area.x2 <= x2 and area.y1 >= y1 and area.y2 <= y2:
			# The area is enclosed.
			penalty_area = 0
		elif area.x2 < x1 or area.x1 > x2 or area.y2 < y1 or area.y1 > y2:
			penalty_area = area.area
		else:
			penalty_area = area.area - (min(area.x2 - x1, x2 - area.x1, area.width) * min(area.y2 - y1, y2 - area.y1, area.height))
		return penalty_area / area.priority
	
	for x in range(im.size[0] - width + 1):
		for y in range(im.size[1] - height + 1):
			penalty = 0
			for area in protected:
				penalty += get_penalty(area, x, y)
			
			if min_penalty is None or penalty < min_penalty:
				min_penalty = penalty
				coords = [(x, y)]
			elif penalty == min_penalty:
				coords.append((x, y))
	
	return coords


def get_crop(im, width=None, height=None, x=None, y=None, protected=None):
	dimensions = get_resize_dimensions(im, width, height)
	
	if dimensions is None:
		return None
	
	width, height = im.size
	new_width, new_height = dimensions
	
	if new_width > width or new_height > height:
		new_width, new_height = get_crop_dimensions(im, (new_width, new_height))
	
	if not protected:
		if x is None:
			x = (width - new_width)/2
			y = (height - new_height)/2
	else:
		coords = get_optimal_crop_dimensions(im, new_width, new_height, protected)
		x, y = coords[0]
	
	x2 = x + new_width
	y2 = y + new_height
	
	if x2 > width or y2 > height:
		raise ResizeError
	
	return x, y, x2, y2


def crop(im, width=None, height=None, x=None, y=None, protected=None):
	"""Returns a cropped copy of the image, preserving any protected areas
	passed in. A ResizeError will be raised if the areas cannot be protected
	with the given crop parameters.
	
	protected is an iterable of ProtectedArea instances. These may or may not be
	tied to an Image instance.
	"""
	im = im.copy()
	
	crop = get_crop(im, width, height, x, y, protected)
	
	if crop is None:
		return im
	
	return im.crop(crop)


### Crop and scale
def crop_and_scale(im, width=None, height=None, x=None, y=None, protected=None):
	im = im.copy()
	dim = get_crop_dimensions(im, (width, height), protected=protected)
	im = crop(im, dim[0], dim[1], protected=protected)
	return scale(im, width, height)


### Seam carving functions
"""
This uses Sameep Tandon's seam carving implementation.
https://github.com/sameeptandon/python-seam-carving/

This is extremely slow. Possible optimization would be to use
brain recall's CAIR: http://sites.google.com/site/brainrecall/cair
This is written in C++ and is much faster. It's unclear whether
cair can modify non-bmp files, though...
"""
try:
	from CAIS import *
except:
	pass
else:
	# It should be possible to add high-energy areas, but how? I would need to
	# track them throughout the resize process, I think.
	def seam_carve(im, width=None, height=None):
		im = im.copy()
		dimensions = get_resize_dimensions(im, width, height)
		
		if dimensions is None or dimensions == im.size:
			return im
		
		width, height = im.size
		x, y = dimensions
		
		while width > x:
			u = find_vertical_seam(gradient_filter(grayscale_filter(im)))
			im = delete_vertical_seam(im, u)
			width = im.size[0]
		
		while width < x:
			u = find_vertical_seam(gradient_filter(grayscale_filter(im)))
			im = add_vertical_seam(im, u)
			width = im.size[0]
		
		while height > y:
			u = find_horizontal_seam(gradient_filter(grayscale_filter(im)))
			im = delete_horizontal_seam(im, u)
			height = im.size[1]
		
		while height < y:
			u = find_horizontal_seam(gradient_filter(grayscale_filter(im)))
			im = add_horizontal_seam(im, u)
			height = im.size[1]
		
		return im