from PIL import Image,  ImageOps, ImageFilter
import StringIO
from pygram.filters import *

def make_linear_ramp(white):
	ramp = []
	r, g, b = white
	for i in range(255):
		ramp.extend((r*i/255, g*i/255, b*i/255))
	return ramp


def pondeye_image_filter(image_file, image_field):
	f = Lomo(image_field.name, file_bytes=image_file)
	f.apply()
	im = Image.open(image_file)
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
	new_image_file = StringIO.StringIO()
	imout.save(new_image_file, "JPEG", quality=90)
	return new_image_file
