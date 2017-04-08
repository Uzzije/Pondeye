PyGram
=================

Instagram-like image filters.


## Usage

First, import the client:

	from filters import *

Instanciate a filter and apply it:

	f = Nashville("image.jpg")
	f.apply()

Available filters: 

- Gotham
- Kelvin
- Lomo
- Nashville
- Toaster

**Note** The filters change the image in-place. Be sure to copy it before applying any filter if you want to copy the original image.


# Tests

Run the tests with:

	python test.py
	
## Tutorial
  
  Instagram Filters with Python(http://pypix.com/python/instagram-filters-python/)

