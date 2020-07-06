import numpy as np

from .function import BaseToolFunction

class BaseToolGaussians (BaseToolFunction) :

    def __init__(self, spectrum):

        super(BaseToolGaussians, self).__init__(spectrum)

    def gaussian(self, x, amplitude, x0, stddev):

        return amplitude * np.exp( - (x-x0)**2 / (2*stddev**2) )

    def gaussian_der(self, x, amplitude, x0, stddev):

        return [
            self.gaussian(x, amplitude, x0, stddev) / amplitude,
            self.gaussian(x, amplitude, x0, stddev) * (x-x0) / stddev**2,
            self.gaussian(x, amplitude, x0, stddev) * (x-x0)**2 / stddev**3,
        ]

    def gaussians(self, x, continuum, amplitudes, x0s, stddevs):

        y = np.poly1d(continuum)(x)
        for args in zip(amplitudes,x0s,stddevs):
            y += self.gaussian(x, *args)

        return y

    def gaussians_der(self, x, continuum, amplitudes, x0s, stddevs):

        jac = [x/x, x]
        for args in zip(amplitudes,x0s,stddevs):
            jac += self.gaussian_der(x, *args)

        return np.array(jac)
