import numpy as np

from scipy.signal import convolve

from ..base import BaseSmoother

class Boxcar (BaseSmoother) :

    NAME = __name__.split('.',2)[2]
    PARAMETERS = 'width',
    DEPENDENCIES = ()

    def set_spectrum(self, spectrum):

        super(Boxcar, self).set_spectrum(spectrum)

        self.flagged = []

    def window(self, width):

        window = np.zeros(self.spectrum.N)
        box, tail = int(width), (width % 1) / 2

        if len(window) % 2 != box % 2:
            box -= 1
            tail += .5

        start = (len(window)-box) // 2
        stop = start + box

        window[start:stop] = 1
        window[start-1] = window[stop] = tail

        return window / np.sum(window)

    def auto(self):

        width = len(self.spectrum.wave) / 100.
        return dict(width=width)

    def __call__(self, width, flagged=None):

        self.width = width
        self.flagged = flagged if not flagged is None else self.flagged

        i = self.get_mask()
        flux = np.interp(self.spectrum.wave, self.spectrum.wave[i], self.spectrum.flux[i])

        window = self.window(width)
        smooth = convolve(flux, window, 'same')

        return smooth
