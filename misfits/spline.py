import numpy as np

from scipy.interpolate import UnivariateSpline

from .errors import SpectrumError, SplineError

class Spline (object) :

    def __init__(self, spectrum):

        self.spectrum = spectrum

        if spectrum._smooth is None:
            raise SpectrumError('smoothed spectrum is needed for spline')

        self.spline = [
            UnivariateSpline(self.spectrum.wave, self.spectrum.smooth, k=3, s=0),
            UnivariateSpline(self.spectrum.wave, self.spectrum.smooth, k=4, s=0).derivative(1),
            UnivariateSpline(self.spectrum.wave, self.spectrum.smooth, k=5, s=0).derivative(2)
        ]

        self._extrema, self._inflection_points = None, None
        self._minima, self._maxima, self._shoulders = None, None, None

    @property
    def extrema(self):

        if self._extrema is None:
            self._extrema = self.spline[1].roots()

        return self._extrema

    @property
    def inflection_points(self):

        if self._inflection_points is None:
            self._inflection_points = self.spline[2].roots()

        return self._inflection_points

    @property
    def minima(self):

        if self._minima is None:
            self._minima = self.extrema[self.spline[2](self.extrema)>0]

        return self._minima

    @property
    def maxima(self):

        if self._maxima is None:
            self._maxima = self.extrema[self.spline[2](self.extrema)<0]

        return self._maxima

    @property
    def shoulders(self):

        if self._shoulders is None:

            self._shoulders = []
            for w0, ww in zip(self.extrema[:-1], self.extrema[1:]):
                i = np.where( (w0 <= self.inflection_points) & (self.inflection_points <= ww) )[0]
                self._shoulders += list(self.inflection_points[i[1::2]]) if len(i) > 1 else []

            self._shoulders = np.array(self._shoulders)

        return self._shoulders

    def __getitem__(self, key):

        if not key in range(3):
            raise SplineError('only 0, 1 and 2-order derivative available')

        return self.spline[key]
