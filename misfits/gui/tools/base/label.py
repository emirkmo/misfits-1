import numpy as np

from .base import Base

class BaseLabel (Base) :

    def __init__(self, parent):

        Base.__init__(self, parent)
        self.intervals, self.interval = parent.intervals, parent.interval
        self.parent = parent

        self._data = ''
        self.artist = self.ax[1].text(0, 0, s='    ', ha='center', va='center',
                                      rotation=90, family='monospace', fontsize=9,
                                      picker=True, zorder=100)
        bbox = dict(ec='black', fc='white', alpha=.7, pad=2)
        self.artist.set_bbox(bbox)

        self.offset = 15

    def update(self):

        x, y = self.parent.x, self.parent.y
        midyaxis = np.mean(self.ax[1].get_ylim())

        va, d = ('bottom', +self.offset) if y < midyaxis else ('top', -self.offset)
        self.artist.set_verticalalignment(va)

        x, y = self.ax[1].transData.transform((x, y))
        x, y = self.ax[1].transData.inverted().transform((x, y + d))

        self.set_position(x, y)

    def set_position(self, x, y):

        self.artist.set_x(x)
        self.artist.set_y(y)

    def set_data(self, data):

        self._data = data
        self.artist.set_text(data.rjust(4))

    @property
    def data(self):

        return self._data if self._data != '' else None

    def validate(self, data):

        if not len(data) or data[-1] in map(chr, range(32,127)):
            return True

    def set_visible(self, visible):

        self.artist.set_visible(visible)

    def delete(self):

        self.ax[1].texts.remove(self.artist)

class BaseFloatLabel (BaseLabel) :

    @property
    def data(self):

        return float(self._data) if self._data != '' else None

    def validate(self, data):

        if not len(data):
            return True
        elif data[-1] == ' ':
            return False

        try:
            assert(float(data) > 0)
        except (AssertionError, ValueError):
            return False
        else:
            return True
