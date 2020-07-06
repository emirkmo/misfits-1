import numpy as np

from .base import Base

class BaseConnection (Base) :

    def __init__(self, parent):

        Base.__init__(self, parent)

        self.x0, self.y0, self.xx, self.yy = None, None, None, None
        self.artist, = self.ax[1].plot([], [], color='black', ls='dashed', picker=True)

    def set_data(self, x0=None, y0=None, xx=None, yy=None):

        self.x0 = x0 if not x0 is None else self.x0
        self.y0 = y0 if not y0 is None else self.y0
        self.xx = xx if not xx is None else self.xx
        self.yy = yy if not yy is None else self.yy

        self.artist.set_data(*zip(*self.data))

    @property
    def data(self):

        data = [(self.x0, self.y0), (self.xx, self.yy)]
        return sorted(data, key=lambda p: p[0] if p[0] is not None else np.inf)

    def set_color(self, color):

        self.artist.set_color(color)

    def set_visible(self, visible):

        self.artist.set_visible(visible)

    def delete(self):

        self.ax[1].lines.remove(self.artist)
