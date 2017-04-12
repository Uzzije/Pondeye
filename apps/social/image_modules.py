from PIL import Image,  ImageOps, ImageFilter
import StringIO
from pygram.filters import *
from global_variables import CURRENT_URL
from django.core.files import temp as tempfile
from django.conf import settings


def make_linear_ramp(white):
	"""
	A more manual way of distorting RGB values of the image.
	Currently not using it.
	:param white:
	:return:
	"""
	ramp = []
	r, g, b = white
	for i in range(255):
		ramp.extend((r*i/255, g*i/255, b*i/255))
	return ramp


def pondeye_image_filter(filename):
	"""
	Apply movie like filter to image
	:param filename:
	:return:
	"""
	temp_path = settings.MEDIA_ROOT + "/" + filename
	f = Lomo(temp_path)
	f.apply()
	image = Image.open(temp_path)
	max_size = (250, 250)
	image.thumbnail(max_size, Image.ANTIALIAS)
	imout = image.filter(ImageFilter.DETAIL)
	imout.save(temp_path, 'JPEG', quality=90)
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
