from collections import OrderedDict

import numpy as np

from .... import SpectrumError

from .base import Base

class BaseInterval (Base) :

    def __init__(self, intervals):

        Base.__init__(self, intervals)
        self.intervals = intervals

        self.x0, self.xx = None, None
        self.artist = self.ax[0].axvspan(None, None, lw=.5, ec='black', alpha=.5,
                                         picker=True)

        self.artists = dict()
        self.artists['spectrum'], = self.ax[1].plot([], [], color='black')

        self.objects = []

        self._cids = OrderedDict()

        try:
            self.spectrum.smooth
        except SpectrumError:
            pass
        else:
            self.artists['smooth'], = self.ax[1].plot([], [], color='black')
            self.artists['spectrum'].set_alpha(.5)
            self.artists['spectrum'].zoom_ignore = True

    def mpl_connect(self, s, func):

        if (s, func) in self._cids:
            return

        cid = self.fig.canvas.mpl_connect(s, func)
        self._cids[(s, func)] = cid

    def mpl_disconnect(self):

        for (s, func), cid in self._cids.items():

            if not cid:
                continue

            self.fig.canvas.mpl_disconnect(cid)
            self._cids[(s, func)] = None

    def mpl_reconnect(self):

        for (s, func), cid in self._cids.items():

            if cid:
                continue

            cid = self.fig.canvas.mpl_connect(s, func)
            self._cids[(s, func)] = cid

    def set_data(self, x0=None, xx=None, cosmetic=False):

        x0 = self.x0 if x0 is None else x0
        xx = self.xx if xx is None else xx

        if not cosmetic:
            self.x0, self.xx = x0, xx
        x0, xx = sorted([x0, xx])

        self.artist.set_xy([(x0, 0), (x0, 1), (xx, 1), (xx, 0)])

        s = self.spectrum(x0, xx)
        self.artists['spectrum'].set_data(s.wave, s.flux)
        if 'smooth' in self.artists:
            self.artists['smooth'].set_data(s.wave, s.smooth)

    @property
    def data(self):

        return sorted([self.x0, self.xx])

    def in_interval(self, x):

        x0, xx = self.data

        if x0 < x <  xx:
            return True
        if not x0 is xx:
            return False

        delta = 3 * np.diff(self.spectrum.wave).mean()
        return np.abs(x - x0) < delta

    def set_color(self, color):

        self.artist.set_facecolor(color)

    def set_visible(self, visible):

        for name, artist in self.artists.items():
            artist.set_visible(visible)

        if visible:
            self.mpl_reconnect()
        else:
            self.mpl_disconnect()

    def delete(self):

        self.ax[0].patches.remove(self.artist)

        for name, artist in self.artists.items():

            if artist in self.ax[1].lines:
                self.ax[1].lines.remove(artist)
            elif artist in self.ax[1].patches:
                self.ax[1].patches.remove(artist)
            else:
                artist.delete()

        self.mpl_disconnect()

    def __iter__(self):

        return iter(self.objects)
