from pygram import PyGram
from decorations.frame import Frame

class Kelvin(PyGram, Frame):

	def apply(self):
		self.execute("convert \( {filename} -auto-gamma -modulate 120,50,100 \) \( -size {width}x{height} -fill 'rgba(255,153,0,0.5)' -draw 'rectangle 0,0 {width},{height}' \) -compose multiply {filename}")
		self.frame("Kelvin.jpg")