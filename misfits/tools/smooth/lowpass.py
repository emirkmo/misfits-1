import numpy as np

from scipy.fft import dct, idct
from scipy.optimize import minimize
from scipy.signal import medfilt

from ..base import BaseSmoother

class LowPass (BaseSmoother) :

    NAME = __name__.split('.',2)[2]
    PARAMETERS = 'signal', 'noise', 'slope', 'flagged'
    DEPENDENCIES = ()

    def set_spectrum(self, spectrum):

        super(LowPass, self).set_spectrum(spectrum)

        self.flagged, self._flagged = [], None
        self.calculate_power_spectrum()

    def power_spectrum_fit_function(self, x, signal, noise, slope):

        y = np.zeros_like(x) + noise
        i = np.where(x < signal/1.5)
        y[i] = slope*(x[i]-signal/1.5) + noise

        return y

    def auto(self):

        lpwrs = np.log10(np.convolve(medfilt(self.pwr, 3), np.ones(7)/7., 'same'))
        fmin = lambda args: np.sum((lpwrs - self.power_spectrum_fit_function(self.bins, *args))**2)
        
        signal = np.where(lpwrs < np.median(self.lpwr))[0][0]
        noise = np.median(self.lpwr)
        slope = (noise - np.max(self.lpwr)) / signal
        signal, noise, slope = minimize(fmin, [signal, noise, slope], method='Nelder-Mead').x

        if signal < 1 or signal >= self.spectrum.N or not np.isfinite(noise):
            signal = int(.1*self.spectrum.N)
        if noise<np.min(self.lpwr) or noise>np.max(self.lpwr) or not np.isfinite(noise):
            noise = np.median(self.lpwr)

        return dict(signal=int(signal), noise=noise, slope=slope)

    def calculate_power_spectrum(self):

        if self.flagged == self._flagged:
            return
        self._flagged = self.flagged.copy()

        i = self.get_mask()
        flux = np.interp(self.spectrum.wave, self.spectrum.wave[i], self.spectrum.flux[i])
        self.p = np.poly1d(np.polyfit(self.spectrum.wave, flux, 2))
        self.ft = dct(flux/self.p(self.spectrum.wave), norm='ortho')

        self.bins = np.arange(self.spectrum.N)
        self.pwr = self.ft**2
        self.lpwr = np.log10(self.pwr)
  
    def __call__(self, signal, noise, slope=np.nan, flagged=None):

        self.flagged = flagged if not flagged is None else self.flagged
        self.calculate_power_spectrum()

        self.signal, self.noise = signal, noise

        lpwr0 = np.log10(np.mean(self.pwr[:signal*2//3])*2)
        self.slope = slope if np.isfinite(slope) else (self.lpwr[signal] - lpwr0) / signal
        s = np.power(10, lpwr0 + self.slope * self.bins)
        ff = s / (s + 10**noise)

        smooth = idct(self.ft*ff, norm='ortho') * self.p(self.spectrum.wave)

        return smooth
