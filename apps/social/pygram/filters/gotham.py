from pygram import PyGram
from decorations.border import Border


class Gotham(PyGram, Border):
    def apply(self):
        self.execute(
            "convert {filename} -modulate 120,10,100 -fill '#222b6d' -colorize 20 -gamma 0.5 -contrast -contrast {filename}")
        self.border()
