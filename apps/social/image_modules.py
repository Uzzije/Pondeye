from PIL import Image,  ImageOps, ImageFilter
import StringIO
from pygram.filters import *
from global_variables import CURRENT_URL


def make_linear_ramp(white):
	ramp = []
	r, g, b = white
	for i in range(255):
		ramp.extend((r*i/255, g*i/255, b*i/255))
	return ramp


def pondeye_image_filter(filename):
	filename_url = CURRENT_URL + filename
	f = Lomo(filename_url)
	f.apply()
	im = Image.open(filename_url)
	imout = im.filter(ImageFilter.DETAIL)
	'''
	im_format = im.format
	#convert to grayscale
	if im.mode != "L":
		im = im.convert("L")
	#optional: apply constrast enhancement here, e.g.
	im = ImageOps.autocontrast(im)

	#apply sepia palette
	im.putpalette(sepia)

	# convert back to RGB so we can save it as JPEG
	# (alternatively, save it in PNG or similar)
	im = im.convert("RGB")
	'''
	new_image_file = filename_url
	imout.save(new_image_file, "JPEG", quality=90)
	return new_image_file
