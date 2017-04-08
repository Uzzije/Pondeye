from ..pygram import PyGram
from ..decorations.frame import Frame


class Nashville(PyGram, Frame):

	def apply(self):
		self.colortone('#222b6d', 50, 0)
		self.colortone('#f7daae', 120, 1)
		self.execute("convert {filename} -contrast -modulate 100,150,100 -auto-gamma {filename}")
		self.frame("Nashville.jpg")