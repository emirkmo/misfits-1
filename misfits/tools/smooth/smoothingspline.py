import numpy as np

from scipy.interpolate import UnivariateSpline

from ..base import BaseSmoother

class SmoothingSpline (BaseSmoother) :

    NAME = __name__.split('.',2)[2]
    PARAMETERS = 'flagged',
    DEPENDENCIES = 'spectrum.error'

    def set_spectrum(self, spectrum):

        super(SmoothingSpline, self).set_spectrum(spectrum)

        self.flagged, self._flagged = [], None

    def __call__(self, flagged=None):

        self.flagged = flagged if not flagged is None else self.flagged

        i = self.get_mask()

        us = UnivariateSpline(self.spectrum.wave[i],
                              self.spectrum.flux[i],
                              1 / self.spectrum.error[i])

        return us(self.spectrum.wave)
