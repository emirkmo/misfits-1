from inspect import stack
from copy import deepcopy

import numpy as np

from ..base import BaseTool

class Minima (BaseTool) :

    NAME = __name__.split('.',2)[2]
    PARAMETERS = 'limits', 'wavelengths', 'references'
    DEPENDENCIES = 'method.smooth',

    def set_spectrum(self, spectrum):

        # make sure spectrum is smoothed
        spectrum.smooth

        super(Minima, self).set_spectrum(spectrum)

    def locations(self):

        f = lambda w: (w, float(self.spectrum.spline[0](w)))
        return self._map_nested_lists(f, self.wavelengths)

    def transform(self, wavelength, reference):

        if reference is not None:

            velocity = list((np.array(wavelength) / reference - 1) * 299792.458)
            units = 'km/s'

        else:

            velocity = wavelength
            units = ''

        return velocity, units

    def continuum_error(self, limits, wavelengths, references):

        smooth = self.spectrum.smooth

        def _(self):

            s = self.spectrum(*limits[stack()[1][0].f_locals['i']])

            loc = np.mean(s.flux)
            scale = np.abs(loc) * s.continuum_error

            (x0, xx), (y0, yy) = s.wave[[0,-1]], np.random.normal(loc, scale, size=2)
            continuum = np.poly1d(np.polyfit([x0, xx], [y0, yy], deg=1))
            self.spectrum.set_smooth(smooth - continuum(self.spectrum.wave))

            extrema = self.spectrum.spline[1].roots()
            minima = extrema[self.spectrum.spline[2](extrema)>0]

            return minima

        minima = self.spectrum.spline.__class__.minima
        self.spectrum.spline.__class__.minima = property(_)

        yield self, limits, wavelengths, references

        self.spectrum.spline.__class__.minima = minima
        self.spectrum.set_smooth(smooth)

    @BaseTool.iterator_modifier(continuum_error)
    def __call__(self, limits, wavelengths, references):

        wavelength = deepcopy(wavelengths)

        for i in range(len(limits)):

            org_waves, new_waves = list(wavelengths[i]), [None]*len(wavelengths[i])

            minima = self.spectrum.spline.minima
            j = np.where( (limits[i][0] <= minima) & (minima <= limits[i][1]) )
            minima = list(minima[j])

            while len(minima) and not all(w is None for w in org_waves):

                def _(k):
                    l = np.argmin((np.array(minima)-org_waves[k])**2)
                    return (minima[l]-org_waves[k])**2, k, l
                res = [_(k) for k,w in enumerate(org_waves) if not w is None]

                k, l = min(res, key=lambda r:r[0])[1:]
                org_waves[k], new_waves[k] = None, minima.pop(l)

            wavelengths[i] = new_waves

        self.set_parameters(limits=limits, wavelengths=wavelengths, references=references)

        return wavelengths, None, None
