import sys

import numpy as np

from scipy.interpolate import UnivariateSpline

from .spline import Spline
from .errors import SpectrumError

class Spectrum (object) :

    def __init__(self, wave, flux, error=None, smooth=None, z=0, continuum_error=0):

        self._wave = np.array(wave)

        if len(self._wave.shape) > 1:
            raise SpectrumError('wavelengh is not 1d')

        self.set_flux(flux)
        self.set_redshift(z) # XXX defines self.wave
        self.set_continuum_error(continuum_error)

        self.N = len(self._wave)

        self.set_error(error)
        self.set_smooth(smooth)

    def set_flux(self, flux):

        flux = np.array(flux)

        if (~np.isfinite(flux)).any():
            raise SpectrumError('spectrum include non-finite number')
        elif self._wave.shape != flux.shape:
            raise SpectrumError('wavelengh and flux dimensions doesn\'t match')

        self.flux = flux
        self._smooth, self._spline, self._continuum = None, None, None

    def set_redshift(self, z):

        self.z = z
        self.wave = self._wave.copy() / (1+z)

    def set_continuum_error(self, continuum_error):

        self.continuum_error = continuum_error

    @property
    def spline(self):

        if self._spline is None:
            self._spline = Spline(self)

        return self._spline

    @property
    def continuum(self):

        if self._continuum is None:
            self._continuum = np.poly1d(np.polyfit(self.wave, self.flux, 2))

        return self._continuum

    @property
    def error(self):

        if not self._error is None:
            return self._error
        else:
            raise SpectrumError('spectrum doesn\'t include errors')

    def set_error(self, error):

        error = np.array(error)

        if error is None or not error.any() or np.isnan(error).all():
            self._error = None
        elif (~np.isfinite(error)).any():
            raise SpectrumError('error spectrum include non-finite value')
        elif error.shape != self._wave.shape:
            raise SpectrumError('error spectrum doesn\'t fit spectrum')
        else: self._error = error

    @property
    def smooth(self):

        if not self._smooth is None:
            return self._smooth
        else:
            raise SpectrumError('spectrum doesn\'t include smoothed spectrum')

    def set_smooth(self, smooth):

        smooth = np.array(smooth)

        if smooth is None or not smooth.any() or np.isnan(smooth).all():
            self._smooth = None
        elif smooth.shape != self._wave.shape:
            raise SpectrumError('smoothed spectrum doesn\'t fit spectrum')
        else:
            self._smooth = smooth

        self._spline = None

    def sample(self):

        return self.flux + self.error * np.random.random(self.N)

    def __call__(self, start=None, stop=None):

        start = start if not start is None else self.wave[ 0]
        stop  = stop  if not stop  is None else self.wave[-1]

        i = np.where( (start <= self.wave) & (self.wave <= stop) )

        error  =  self._error[i] if not self._error  is None else None
        smooth = self._smooth[i] if not self._smooth is None else None

        return type('subspectrum', (object,), dict(
            wave = self.wave[i], flux = self.flux[i],
            error = error, smooth = smooth, z = self.z,
            continuum_error = self.continuum_error
        ))

    def __getitem__(self, i):

        try:
            return self.wave[i], self.flux[i]
        except IndexError as e:
            pass

        try:
            i = np.argmin((self.wave - i)**2)
        except ValueError:
            raise e
        else:
            return self.wave[i], self.flux[i]

    def save(self, header, filename=None):

        if filename is None:
            filename = sys.stdout

        output = [self.wave, self.flux]

        try:
            output.append(self.error)
        except SpectrumError:
            output.append(np.nan*np.ones(self.N))

        try:
            output.append(self.smooth)
        except SpectrumError:
            output.append(np.nan*np.ones(self.N))

        np.savetxt(filename, np.transpose(output), header=header)
