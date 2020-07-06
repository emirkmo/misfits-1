from .base import Base
from .label import BaseLabel

class BasePoint (Base) :

    def __init__(self, parent):

        Base.__init__(self, parent)
        self.intervals, self.interval = parent.intervals, parent.interval
        self.parent = parent

        self.x, self.y = None, None
        self.artist, = self.ax[1].plot([], [], ms=10, marker='o', mew=1.5, mec='black',
                                       mfc='white', alpha=.6, picker=5, zorder=float('inf'))

    def set_data(self, x=None, y=None):

        self.x = x if not x is None else self.x
        self.y = y if not y is None else self.y

        x = self.x if not self.x is None else []
        y = self.y if not self.y is None else []

        self.artist.set_data(x, y)

    def set_color(self, color):

        self.artist.set_markerfacecolor(color)

    def set_visible(self, visible):

        self.artist.set_visible(visible)

    def delete(self):

        self.ax[1].lines.remove(self.artist)

class BaseTogglePoint (BasePoint) :

    def __init__(self, parent):

        BasePoint.__init__(self, parent)

        self.artist.set_picker(5)

        self.selected = False

    def toggle(self):

        self.selected = bool((self.selected + 1) % 2)

class BaseLabelTogglePoint (BaseTogglePoint) :

    def __init__(self, parent):

        BaseTogglePoint.__init__(self, parent)

        self.label = self.def_label()
        self.label.set_visible(False)

    def def_label(self):

        return BaseLabel(self)

    def toggle(self):

        BaseTogglePoint.toggle(self)

        if self.selected:
            self.label.update()
            self.label.set_visible(True)
        else:
            self.label.set_visible(False)

    def set_visible(self, visible):

        BaseTogglePoint.set_visible(self, visible)

        self.label.set_visible(visible)

    def delete(self):

        BaseTogglePoint.delete(self)

        self.label.delete()
