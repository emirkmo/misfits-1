import numpy as np

from scipy.interpolate import UnivariateSpline

from ..base import BaseTool
from . import pEW

class ShallowpEW (pEW) :

    NAME = __name__.split('.',2)[2]
    PARAMETERS = 'limits', 'continua'
    DEPENDENCIES = ()

    def set_spectrum(self, spectrum):

        BaseTool.set_spectrum(self, spectrum)

    def locations(self):

        f = lambda w: (np.mean(w), np.mean(self.spectrum(w[1],w[-2]).flux))
        return self._map_nested_lists(f, self.continua)

    def pew(self, spectrum, ap0, ap1):

        p = np.poly1d(np.polyfit(*zip(*[ap0, ap1]), deg=1))
        w = 1 - spectrum.flux / p(spectrum.wave)

        return UnivariateSpline(spectrum.wave, w, k=1, s=0).integral(ap0, ap1)

    def continuum_error(self, limits, continua):

        flux = self.spectrum.flux[:]
        scale = self.spectrum.continuum_error

        self.spectrum.flux = type('weirdo', (), dict(
            __getitem__ = lambda _, i: flux[i] * (1 + np.random.normal(0, scale)),
            __truediv__ = lambda _, v: flux / v, __div__ = lambda _, v: 1. * flux / v
        ))()

        yield self, limits, continua

        self.spectrum.flux = flux

    @BaseTool.iterator_modifier(continuum_error)
    def __call__(self, limits, continua):

        widths = []

        for i in range(len(limits)):

            widths.append([])

            for j in range(len(continua[i])):

                ap = []

                for x0,xx in [continua[i][j][k*2:(k+1)*2] for k in range(2)]:

                    s = self.spectrum(x0, xx)
                    x, y, xmean = s.wave, s.flux, np.mean([x0,xx])

                    try:
                        ymean = np.polyval(np.polyfit(x, y, 1), xmean)
                    except:
                        ymean = self.spectrum[xmean][1]

                    ap.append((xmean,ymean))

                widths[-1].append(self.pew(self.spectrum, *ap))

        self.set_parameters(limits=limits, continua=continua)

        return widths, None, None
