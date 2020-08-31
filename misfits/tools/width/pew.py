from copy import deepcopy

import numpy as np

from scipy.interpolate import UnivariateSpline

from ..base import BaseTool

class pEW (BaseTool) :

    NAME = __name__.split('.',2)[2]
    PARAMETERS = 'limits', 'maxima'
    DEPENDENCIES = 'method.smooth',

    def set_spectrum(self, spectrum):

        # make sure spectrum is smoothed
        spectrum.smooth

        super(pEW, self).set_spectrum(spectrum)

    def locations(self):

        f = lambda w: (np.mean(w), np.mean(self.spectrum(*w).smooth))
        return self._map_nested_lists(f, self.maxima)

    def pew(self, p0, p1):

        p0 = p0 if not isinstance(p0, float) else (p0, self.spectrum.spline[0](p0))
        p1 = p1 if not isinstance(p1, float) else (p1, self.spectrum.spline[0](p1))

        c = np.poly1d(np.polyfit(*zip(*[p0, p1]), deg=1))
        f = 1 - self.spectrum.flux / c(self.spectrum.wave)

        pew = UnivariateSpline(self.spectrum.wave, f, k=1, s=0).integral(p0, p1)

        f = self.spectrum.error**2 / c(self.spectrum.wave)**2

        i = np.arange(self.spectrum.N)
        dw = UnivariateSpline(i, self.spectrum.wave).derivative()(i)

        var = UnivariateSpline(self.spectrum.wave, f * dw, k=1, s=0).integral(p0, p1)

        return pew, np.sqrt(var)

    def continuum_error(self, limits, maxima):

        spline0 = self.spectrum.spline[0]

        loc = lambda w: spline0(w)
        scale = lambda w: np.abs(loc(w)) * self.spectrum.continuum_error

        self.spectrum.spline.spline[0] = lambda w: np.random.normal(loc(w), scale(w))

        yield self, limits, maxima

        self.spectrum.spline.spline[0] = spline0

    @BaseTool.iterator_modifier(continuum_error)
    def __call__(self, limits, maxima):

        flux = self.spectrum.flux
        self.spectrum.flux = self.spectrum.smooth

        widths, stddevs, maxima = [], [], deepcopy(maxima)

        for i in range(len(limits)):

            widths.append([])
            stddevs.append([])

            _maxima = self.spectrum.spline.maxima
            j = np.where( (limits[i][0] <= _maxima) & (_maxima <= limits[i][1]) )
            _maxima = _maxima[j]

            for j, (w0, ww) in enumerate(maxima[i]):

                w0 = _maxima[np.argmin((_maxima - w0)**2)]
                ww = _maxima[np.argmin((_maxima - ww)**2)]

                width, stddev = self.pew(w0, ww)
                widths[-1].append(width)
                stddevs[-1].append(stddev)

                maxima[i][j] = w0, ww

        self.spectrum.flux = flux

        self.set_parameters(limits=limits, maxima=maxima)

        return widths, stddevs, None
