#from filters import *
"""
f = Lomo('tests/test-look3.jpg')
f.apply()

f = Lomo('tests/test-look2.jpg')
f.apply()
"""

from PIL import Image, ImageFilter
im = Image.open('http://Uzzije.pythonanywhere.com/media/image/progresspicture/2017/04/08/temp_mpXCe6T.jpeg')
im.show()