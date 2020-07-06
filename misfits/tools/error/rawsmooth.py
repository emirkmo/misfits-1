import numpy as np

from scipy.signal import convolve
from scipy.signal.windows import gaussian
from scipy.optimize import minimize

from ..base import BaseTool

class RawSmooth (BaseTool) :

    NAME = __name__.split('.',2)[2]
    PARAMETERS = 'length', 'flagged'
    DEPENDENCIES = 'spectrum.smooth',

    def set_spectrum(self, spectrum):

        super(RawSmooth, self).set_spectrum(spectrum)

        self.residuals = self.spectrum.flux - self.spectrum.smooth
        self.abs_residuals = np.abs(self.residuals)

        self.flagged = []

    def auto(self):
      
        length = self.spectrum.N / 100

        return dict(length=length)

    def get_mask(self):

        mask = np.ones(self.spectrum.N, dtype=bool)
        if len(self.flagged):
            mask[np.array(self.flagged)] = False

        return mask

    def __call__(self, length, flagged=None):

        self.length = length
        self.flagged = flagged if not flagged is None else self.flagged

        i = self.get_mask()
        abs_residuals = np.interp(self.spectrum.wave, self.spectrum.wave[i], self.abs_residuals[i])

        window = gaussian(self.spectrum.N, length)
        window /= np.sum(window)
        error = convolve(abs_residuals, window, mode='same')
        
        fmin = lambda a: np.power( 1.*np.sum(abs_residuals < a*error) / self.spectrum.N - .682689492137 , 2)
        error *= minimize(fmin, 1, method='Nelder-Mead').x[0]

        return error
