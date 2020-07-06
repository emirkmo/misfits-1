from .base import Base
from .label import BaseLabel

class BaseVariable (Base) :

    def __init__(self, parent):

        Base.__init__(self, parent)
        self.intervals, self.interval = parent.intervals, parent.interval
        self.parent = parent

        self.x, self.y = [], []
        self.artist, = self.ax[1].plot([], [], marker='o', ms=10, mew=1.5,
            mec='black', mfc='white', alpha=.6, picker=5, zorder=99)

    def set_data(self, x=None, y=None):

        self.x = x if not x is None else self.x
        self.y = y if not y is None else self.y

        self.artist.set_data(self.x, self.y)

        self.parent.update()

    def set_color(self, color):

        self.artist.set_markerfacecolor(color)

    def set_visible(self, visible):

        self.artist.set_visible(visible)

    def update(self):

        pass

    def delete(self):

        self.ax[1].lines.remove(self.artist)

class BaseLabelVariable (BaseVariable) :

    def __init__(self, parent):

        BaseVariable.__init__(self, parent)

        self.label = self.def_label()

    def def_label(self):

        return BaseLabel(self)

    def set_data(self, x=None, y=None):

        BaseVariable.set_data(self, x, y)

        self.label.update()

    def set_visible(self, visible):

        BaseVariable.set_visible(self, visible)

        self.label.set_visible(visible)

    def delete(self):

        BaseVariable.delete(self)

        self.label.delete()
