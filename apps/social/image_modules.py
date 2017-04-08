from PIL import Image,  ImageOps

def make_linear_ramp(white):
	ramp = []
	r, g, b = white
	for i in range(255):
		ramp.extend((r*i/255, g*i/255, b*i/255))
	return ramp

def pondeye_image_filter(image_file):
	sepia = make_linear_ramp((255, 240, 192))
	im = Image.open(image_file)

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
	im.save(image_file)
