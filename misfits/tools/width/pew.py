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

    def pew(self, spectrum, w0, ww):

        p = np.poly1d(np.polyfit([w0, ww], list(map(spectrum.spline[0], [w0, ww])), 1))
        w = 1 - spectrum.smooth / p(spectrum.wave)

        return UnivariateSpline(spectrum.wave, w, s=0).integral(w0, ww)

    def continuum_error(self, limits, maxima):

        spline0 = self.spectrum.spline[0]

        loc = lambda w: spline0(w)
        scale = lambda w: np.abs(loc(w)) * self.spectrum.continuum_error

        self.spectrum.spline.spline[0] = lambda w: np.random.normal(loc(w), scale(w))

        yield self, limits, maxima

        self.spectrum.spline.spline[0] = spline0

    @BaseTool.iterator_modifier(continuum_error)
    def __call__(self, limits, maxima):

        widths = []

        for i in range(len(limits)):

            widths.append([])

            _maxima = self.spectrum.spline.maxima
            j = np.where( (limits[i][0] <= _maxima) & (_maxima <= limits[i][1]) )
            _maxima = list(_maxima[j])

            for j, (w0, ww) in enumerate(maxima[i]):

                w0 = _maxima[np.argmin((_maxima - w0)**2)]
                ww = _maxima[np.argmin((_maxima - ww)**2)]

                widths[-1].append(self.pew(self.spectrum, w0, ww))

                maxima[i][j] = w0, ww

        self.set_parameters(limits=limits, maxima=maxima)

        return widths, None, None
