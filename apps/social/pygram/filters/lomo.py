from ..pygram import PyGram
from ..decorations.vignette import Vignette

class Lomo(PyGram, Vignette):

	def apply(self):
		self.execute("convert {filename} -channel R -level 15% -channel G -level 15% {filename}")
		self.vignette()